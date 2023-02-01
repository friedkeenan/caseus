import abc
import asyncio
import io
import random
import pak

from public import public

from ..packets import (
    Packet,
    GenericPacketWithID,
    ServerboundPacket,
    ClientboundPacket,
    serverbound,
    clientbound,
)

from ..secrets import Secrets

from .. import types

@public
class Proxy(pak.AsyncPacketHandler):
    MAIN_SERVER_PORTS_FALLBACK = [11801, 12801, 13801, 14801]

    CORRECT_LOADER_SIZE = 0x7EE88

    # NOTE: Be careful when sending packets to the server with this.
    # Take great care to ensure that the fingerprints of packets
    # would never get out of sync, else the server will kick you.
    #
    # This means that every packet you send to the server, it should be
    # matched up with a packet sent by the client, having the same
    # fingerprint. If that cannot work for you, then you should use
    # 'FingerprintHandlingProxy' instead.

    class _Connection(pak.io.Connection):
        # Used for the 'ServerConnection' and 'ClientConnection'
        # to depend on each other for closing.
        #
        # We make explicit calls to 'Connection' at times to avoid recursion.

        class Pair:
            def __init__(self, *, client, server):
                self.client = client
                self.server = server

        _listen_sequentially = False

        def __init__(self, proxy, *, destination=None, **kwargs):
            self.proxy       = proxy
            self.destination = destination

            super().__init__(ctx=Packet.Context(), **kwargs)

        def _listen(self):
            self._tasks.append(asyncio.create_task(self.proxy._listen_impl(self)))

        def is_closing(self):
            if self.destination is None:
                return pak.io.Connection.is_closing(self)

            return pak.io.Connection.is_closing(self) or pak.io.Connection.is_closing(self.destination)

        def close(self):
            if self.destination is not None:
                pak.io.Connection.close(self.destination)

            pak.io.Connection.close(self)

        async def wait_closed(self):
            if self.destination is not None:
                await pak.io.Connection.wait_closed(self.destination)

            await pak.io.Connection.wait_closed(self)

        async def _replace_packet(self, packet):
            pass

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

        def _written_packet_length(self, data):
            return len(data)

        def _written_packet_data(self, packet):
            return packet.pack(ctx=self.ctx)

        async def write_packet_instance(self, packet):
            packet_data = self._written_packet_data(packet)

            type_ctx = pak.Type.Context(ctx=self.ctx)

            await self.write_data(
                types.VarInt.pack(self._written_packet_length(packet_data), ctx=type_ctx) +

                packet_data
            )

    # TODO: Do some sort of inheritance shenanigans for connections
    # to better support multiple inheritance of proxies? Maybe also
    # allow for 'CommonConnection'.

    class ServerConnection(_Connection):
        @property
        def secrets(self):
            return self.destination.secrets

        @property
        def is_satellite(self):
            return self.destination.is_satellite

        @property
        def main(self):
            return self.destination.main

        @property
        def satellite(self):
            return self.destination.satellite

        @property
        def session_id(self):
            return self.destination.session_id

        async def _replace_packet(self, packet):
            await self.write_packet(
                serverbound.KeepAlivePacket,

                fingerprint = packet.fingerprint,
            )

        # The fingerprint is not included in the packet length.
        def _written_packet_length(self, data):
            return len(data) - 1

        def _written_packet_data(self, packet):
            header = packet.header(ctx=self.ctx)

            packet_body = packet.pack_without_header(ctx=self.ctx)
            packet_body = packet.cipher_data(packet_body, secrets=self.secrets, fingerprint=header.fingerprint)

            return header.pack(ctx=self.ctx) + packet_body

        def _packet_from_data(self, buf):
            header = ClientboundPacket.Header.unpack(buf, ctx=self.ctx)

            packet_cls = ClientboundPacket.subclass_with_id(header.id, ctx=self.ctx)
            if packet_cls is None:
                packet_cls = GenericPacketWithID(header.id, ClientboundPacket)

            return packet_cls.unpack(buf, ctx=self.ctx)

    class ClientConnection(_Connection):
        # We always want to listen sequentially for client
        # connections so that the fingerprints never get
        # out of order when sending them to the server.
        _listen_sequentially = True

        def __init__(self, proxy, *, is_satellite=False, main=None, **kwargs):
            super().__init__(proxy, **kwargs)

            self.secrets = None

            self.is_satellite = is_satellite

            if is_satellite:
                self.main      = main
                self.satellite = self.Pair(client=self, server=None)

                self.proxy.satellite_clients.append(self)
            else:
                self.main      = self.Pair(client=self, server=self.destination)
                self.satellite = None

                self.proxy.main_clients.append(self)

            self.session_id = None

        def close(self):
            try:
                if self.is_satellite:
                    self.proxy.satellite_clients.remove(self)
                else:
                    self.proxy.main_clients.remove(self)

            # We might already have been closed.
            except ValueError:
                pass

            super().close()

        # The fingerprint is not included in the packet length.
        async def _read_length(self):
            reported_length = await super()._read_length()
            if reported_length is None:
                return None

            return reported_length + 1

        def _packet_from_data(self, buf):
            header = ServerboundPacket.Header.unpack(buf, ctx=self.ctx)

            packet_cls = ServerboundPacket.subclass_with_id(header.id, ctx=self.ctx)
            if packet_cls is None:
                packet_cls = GenericPacketWithID(header.id, ServerboundPacket)

            if self.secrets is not None:
                buf = packet_cls.decipher_data(buf, secrets=self.secrets, fingerprint=header.fingerprint)
            elif packet_cls.CIPHER is not None:
                packet_cls = GenericPacketWithID(header.id, ServerboundPacket)

            packet = packet_cls.unpack_with_fingerprint(header.fingerprint, buf, ctx=self.ctx)

            return packet

    REPLACE_PACKET = pak.util.UniqueSentinel("REPLACE_PACKET")
    FORWARD_PACKET = pak.util.UniqueSentinel("FORWARD_PACEKT")
    DO_NOTHING     = pak.util.UniqueSentinel("DO_NOTHING") # TODO: Better name?

    def __init__(
        self,
        *,
        host_address        = None,
        host_main_port      = 11801,
        host_satellite_port = 12801,

        expected_address = "localhost",
    ):
        super().__init__()

        self.host_address        = host_address
        self.host_main_port      = host_main_port
        self.host_satellite_port = host_satellite_port

        self.expected_address = expected_address

        self.main_srv     = None
        self.main_clients = []

        self.satellite_srv     = None
        self.satellite_clients = []

        self._satellite_packets = []

    def register_packet_listener(self, listener, *packet_types, after=False, **flags):
        super().register_packet_listener(listener, *packet_types, after=after, **flags)

    def is_serving(self):
        return (
            self.main_srv      is not None and self.main_srv.is_serving()      and
            self.satellite_srv is not None and self.satellite_srv.is_serving()
        )

    def close(self):
        if self.main_srv is not None:
            self.main_srv.close()

        if self.satellite_srv is not None:
            self.satellite_srv.close()

    async def wait_closed(self):
        if self.main_srv is not None:
            await self.main_srv.wait_closed()

        if self.satellite_srv is not None:
            await self.satellite_srv.wait_closed()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        self.close()
        await self.wait_closed()

    async def _listen_to_nested_packet(self, source_conn, packet, *, after):
        packet = packet.immutable_copy()

        async with self.listener_task_group(listen_sequentially=source_conn._listen_sequentially) as group:
            for listener in self.listeners_for_packet(packet, after=after):
                group.create_task(listener(source_conn, packet))

    async def _listen_to_packet(self, source_conn, packet):
        async with self.listener_task_group(listen_sequentially=source_conn._listen_sequentially) as group:
            before_listeners = self.listeners_for_packet(packet, after=False)
            async def proxy_wrapper():
                results = await asyncio.gather(*[listener(source_conn, packet) for listener in before_listeners])

                if self.REPLACE_PACKET in results:
                    await source_conn.destination._replace_packet(packet)

                elif self.DO_NOTHING not in results:
                    await source_conn.destination.write_packet_instance(packet)

                    after_listeners = self.listeners_for_packet(packet, after=True)
                    await asyncio.gather(*[listener(source_conn, packet) for listener in after_listeners])

            group.create_task(proxy_wrapper())

    async def _listen_impl(self, source_conn):
        while self.is_serving() and not source_conn.is_closing():
            try:
                async for packet in source_conn.continuously_read_packets():
                    packet.make_immutable()

                    await self._listen_to_packet(source_conn, packet)

            finally:
                await self.end_listener_tasks()

    async def listen(self, client):
        client_task = asyncio.create_task(self._listen_impl(client))

        # The server connection gets initialized later.
        while client.destination is None:
            if client.is_closing():
                await client_task

                return

            await pak.util.yield_exec()

        await asyncio.gather(client_task, self._listen_impl(client.destination))

    async def new_main_connection(self, client_reader, client_writer):
        client = self.ClientConnection(self, reader=client_reader, writer=client_writer)

        async with client:
            await self.listen(client)

    async def open_main_server(self):
        return await asyncio.start_server(self.new_main_connection, self.host_address, self.host_main_port)

    def _satellite_info_with_auth_id(self, auth_id):
        for packet, main_client in self._satellite_packets:
            if packet.auth_id == auth_id:
                return packet, main_client

        return None, None

    async def new_satellite_connection(self, client_reader, client_writer):
        client = self.ClientConnection(self, is_satellite=True, reader=client_reader, writer=client_writer)

        async with client:
            await self.listen(client)

    async def open_satellite_server(self):
        return await asyncio.start_server(self.new_satellite_connection, self.host_address, self.host_satellite_port)

    async def open_streams(self, address, ports):
        return await asyncio.open_connection(address, random.choice(ports))

    async def startup(self):
        self.main_srv      = await self.open_main_server()
        self.satellite_srv = await self.open_satellite_server()

    async def on_start(self):
        await asyncio.gather(
            self.main_srv.serve_forever(),
            self.satellite_srv.serve_forever(),
        )

    async def start(self):
        await self.startup()

        async with self:
            await self.on_start()

    def run(self):
        try:
            asyncio.run(self.start())

        except KeyboardInterrupt:
            pass

    @pak.packet_listener(serverbound.HandshakePacket)
    async def _fix_handshake_packet(self, source, packet):
        # With the proxy loader, the loader's stage size will
        # not be what the server expects, so we correct it here.

        corrected = packet.copy()

        corrected.loader_stage_size = self.CORRECT_LOADER_SIZE

        await source.destination.write_packet_instance(corrected)

        return self.DO_NOTHING

    @pak.packet_listener(clientbound.ReaffirmServerAddressPacket)
    async def _protect_proxy_address(self, source, packet):
        # Because we are using a proxy, the client will be
        # connected to a different address than the server
        # will reaffirm. Therefore we intercept this packet
        # and replace the contained address with a more
        # complacent one.

        protected = packet.copy()

        protected.address = self.expected_address

        await source.destination.write_packet_instance(protected)

        return self.DO_NOTHING

    @pak.packet_listener(clientbound.LoginSuccessPacket)
    async def _on_login_success(self, source, packet):
        source.destination.session_id = packet.session_id

    @pak.packet_listener(clientbound.ChangeSatelliteServerPacket)
    async def _proxy_satellite_server(self, source, packet):
        if packet.should_ignore:
            return self.FORWARD_PACKET

        self._satellite_packets.append((packet, source.destination))

        proxied         = packet.copy()
        proxied.address = self.expected_address
        proxied.ports   = [self.host_satellite_port]

        await source.destination.write_packet_instance(proxied)

        return self.DO_NOTHING

    @pak.packet_listener(serverbound.SatelliteHandshakePacket)
    async def _complete_satellite_proxy(self, source, packet):
        original_packet, main_client = self._satellite_info_with_auth_id(packet.auth_id)
        if original_packet is None:
            source.close()

            return

        self._satellite_packets.remove((original_packet, main_client))

        source.main       = source.Pair(client=main_client, server=main_client.destination)
        source.secrets    = main_client.secrets
        source.session_id = main_client.session_id

        server_reader, server_writer = await self.open_streams(original_packet.address, original_packet.ports)
        source.destination = self.ServerConnection(self, destination=source, reader=server_reader, writer=server_writer)

        source.satellite = source.Pair(client=source, server=source.destination)
        main_client.satellite = main_client.Pair(client=source, server=source.destination)

    # Listen to various nested packets.

    @pak.packet_listener(serverbound.TribulleWrapperPacket, clientbound.TribulleWrapperPacket)
    async def _on_tribulle(self, source, packet):
        await self._listen_to_nested_packet(source, packet.nested, after=False)

    @pak.packet_listener(serverbound.LegacyWrapperPacket, clientbound.LegacyWrapperPacket)
    async def _on_legacy(self, source, packet):
        await self._listen_to_nested_packet(source, packet.nested, after=False)

    @pak.packet_listener(serverbound.ExtensionWrapperPacket, clientbound.ExtensionWrapperPacket)
    async def _on_extension(self, source, packet):
        await self._listen_to_nested_packet(source, packet.nested, after=False)

        # Never forward on an extension packet.
        return self.DO_NOTHING

    @pak.packet_listener(serverbound.TribulleWrapperPacket, clientbound.TribulleWrapperPacket)
    async def _on_tribulle_after(self, source, packet):
        await self._listen_to_nested_packet(source, packet.nested, after=True)

    @pak.packet_listener(serverbound.LegacyWrapperPacket, clientbound.LegacyWrapperPacket, after=True)
    async def _on_legacy_after(self, source, packet):
        await self._listen_to_nested_packet(source, packet.nested, after=True)

    @pak.packet_listener(serverbound.ExtensionWrapperPacket, clientbound.ExtensionWrapperPacket, after=True)
    async def _on_extension_after(self, source, packet):
        await self._listen_to_nested_packet(source, packet.nested, after=True)

    @pak.packet_listener(serverbound.KeySourcesPacket)
    async def _load_packet_key_sources(self, source, packet):
        source.secrets = Secrets(packet.packet_key_sources)

    @pak.packet_listener(serverbound.MainServerInfoPacket)
    async def _connect_to_main_server(self, source, packet):
        ports = packet.ports
        if len(ports) == 0:
            ports = self.MAIN_SERVER_PORTS_FALLBACK

        server_reader, server_writer = await self.open_streams(packet.address, ports)
        source.destination = self.ServerConnection(self, destination=source, reader=server_reader, writer=server_writer)

        source.main.server = source.destination
