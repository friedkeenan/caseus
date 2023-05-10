import abc
import asyncio
import io
import pak

from pathlib import Path
from public  import public

# We import these namespace-less to improve
# performance upon importing our library.
from scapy.layers.inet import TCP, IP
from scapy.sendrecv import AsyncSniffer

from ..packets import (
    Packet,
    ServerboundPacket,
    ClientboundPacket,
    serverbound,
    clientbound,
)

from ..secrets import Secrets

from .. import types

@public
class Sniffer(pak.AsyncPacketHandler):
    MAIN_IP_ADDR = "193.70.81.30"
    MAIN_PORTS   = [11801, 12801, 13801, 14801]

    # TODO: Reduce code duplication between this
    # and the proxy connection classes.
    class _Connection(pak.io.Connection):
        def __init__(self, *, sniffer):
            super().__init__(ctx=Packet.Context())

            self.sniffer = sniffer

        @property
        def secrets(self):
            return self.sniffer.secrets

        async def open_streams(self):
            self.reader = asyncio.StreamReader()
            self.writer = pak.io.ByteStreamWriter()

        def feed_data(self, data):
            self.reader.feed_data(data)

        async def _read_length(self):
            length_data = b""

            type_ctx = pak.Type.Context(ctx=self.ctx)
            while True:
                next_byte = await self.read_data(1)
                if next_byte is None:
                    return None

                length_data += next_byte

                try:
                    return types.VarInt.unpack(length_data, ctx=type_ctx)

                except types.VarNumBufferLengthError:
                    raise

                except asyncio.CancelledError:
                    raise

                except Exception:
                    continue

                break

        @abc.abstractmethod
        def _packet_from_data(self, buf):
            raise NotImplementedError

        async def _read_next_packet(self):
            length = await self._read_length()
            if length is None:
                return None

            data = await self.read_data(length)
            if data is None:
                return None

            buf = io.BytesIO(data)

            return self._packet_from_data(buf)

        async def write_packet_instance(self, packet):
            raise NotImplementedError

    class ClientboundConnection(_Connection):
        def _packet_from_data(self, buf):
            header = ClientboundPacket.Header.unpack(buf, ctx=self.ctx)

            packet_cls = ClientboundPacket.subclass_with_id(header.id, ctx=self.ctx)
            if packet_cls is None:
                packet_cls = ClientboundPacket.GenericWithID(header.id)

            return packet_cls.unpack(buf, ctx=self.ctx)

    class ServerboundConnection(_Connection):
        async def _read_length(self):
            # The fingerprint is not included in the packet length.
            return await super()._read_length() + 1

        @property
        def should_decipher(self):
            return self.secrets is not None

        def _packet_from_data(self, buf):
            header = ServerboundPacket.Header.unpack(buf, ctx=self.ctx)

            packet_cls = ServerboundPacket.subclass_with_id(header.id, ctx=self.ctx)
            if packet_cls is None:
                packet_cls = ServerboundPacket.GenericWithID(header.id)

            if self.should_decipher:
                buf = packet_cls.decipher_data(buf, secrets=self.secrets)
            elif packet_cls.CIPHER is not None:
                packet_cls = ServerboundPacket.GenericWithID(header.id)

            return packet_cls.unpack_with_fingerprint(header.fingerprint, buf, ctx=self.ctx)

    class ServerInfo:
        def __init__(self, name, ip_addr, ports, *, sniffer):
            self.name    = name
            self.ip_addr = ip_addr
            self.ports   = ports

            self.sniffer = sniffer

            self.clientbound = sniffer.ClientboundConnection(sniffer=sniffer)
            self.serverbound = sniffer.ServerboundConnection(sniffer=sniffer)

        async def open_streams(self):
            await self.clientbound.open_streams()
            await self.serverbound.open_streams()

        def connection_for_ip(self, ip):
            if ip.dst == self.ip_addr:
                return self.serverbound

            return self.clientbound

        async def _listen(self):
            await asyncio.gather(
                self.sniffer._listen_to_packets(self, self.clientbound),
                self.sniffer._listen_to_packets(self, self.serverbound),
            )

    def __init__(self, *, key_sources_path=None):
        super().__init__()

        self.secrets = None

        if key_sources_path is not None:
            self._key_sources_path = key_sources_path
            self.register_packet_listener(self._read_key_sources, serverbound.HandshakePacket)

        self.main      = self.ServerInfo("MAIN", self.MAIN_IP_ADDR, self.MAIN_PORTS, sniffer=self)
        self.satellite = self.ServerInfo("SATELLITE", "", [], sniffer=self)

        self.sniffer = AsyncSniffer(
            lfilter = self._should_handle_tcp_packet,
            prn     = self._handle_tcp_packet,
        )

    def _server_info_from_ip(self, ip):
        for server in (self.main, self.satellite):
            if server.ip_addr in (ip.src, ip.dst):
                return server

        return None

    def _should_handle_tcp_packet(self, packet):
        if TCP not in packet:
            return False

        if IP not in packet:
            return False

        tcp = packet[TCP]
        ip  = packet[IP]

        server = self._server_info_from_ip(ip)
        if server is None:
            return False

        if tcp.sport not in server.ports and tcp.dport not in server.ports:
            return False

        if len(tcp.payload) == 0:
            return False

        return True

    def _handle_tcp_packet(self, packet):
        ip = packet[IP]

        server     = self._server_info_from_ip(ip)
        connection = server.connection_for_ip(ip)

        connection.feed_data(bytes(packet[TCP].payload))

    async def _listen_dispatch(self, server, connection, packet, **flags):
        async with self.listener_task_group(listen_sequentially=False) as group:
            for listener in self.listeners_for_packet(packet, **flags):
                group.create_task(listener(server, packet))

    async def _listen_to_packets(self, server, connection):
        async for packet in connection.continuously_read_packets():
            await self._listen_dispatch(server, connection, packet)

    async def _listen_impl(self):
        server_listeners = [
            self.main._listen(),
            self.satellite._listen(),
        ]

        server_listeners = [asyncio.create_task(coro) for coro in server_listeners]

        while not any(task.done() for task in server_listeners):
            await pak.util.yield_exec()

        await asyncio.gather(*server_listeners)

    async def listen(self):
        try:
            await self._listen_impl()

        finally:
            await self.end_listener_tasks()

    def close(self):
        self.sniffer.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    async def startup(self):
        await self.main.open_streams()
        await self.satellite.open_streams()

        self.sniffer.start()

    async def on_start(self):
        await self.listen()

    async def start(self):
        await self.startup()

        with self:
            await self.on_start()

    def run(self):
        try:
            asyncio.run(self.start())

        except KeyboardInterrupt:
            pass

    async def _read_key_sources(self, server, packet):
        with self._key_sources_path.open() as f:
            key_sources = (int(x) for x in f.read().split(","))

        self.secrets = Secrets(key_sources)

    @pak.packet_listener(clientbound.ChangeSatelliteServerPacket)
    async def _change_satellite_server(self, server, packet):
        self.satellite.ip_addr = packet.address
        self.satellite.ports   = packet.ports
