import asyncio
import io
import random
import pak

from public import public

from ..packets import (
    ServerboundPacket,
    serverbound,
    clientbound,
)

from ..secrets import Secrets

from .. import types

@public
class MinimalServer(pak.AsyncPacketHandler):
    MAX_AUTH_TOKEN         = 2**31 - 1
    MAX_VERIFICATION_TOKEN = 2**31 - 1

    class Connection(pak.io.Connection):
        class SynchronizedAttr:
            def __init__(self, initial_value):
                self.initial_value = initial_value

            def __set_name__(self, owner, name):
                self.underlying_attr     = f"_synchronized_{name}"
                self.set_value_flag_attr = f"{self.underlying_attr}_set_value_flag"

            def __get__(self, instance, owner=None):
                if instance is None:
                    return self

                if not hasattr(instance.main, self.set_value_flag_attr):
                    self.__set__(instance, self.initial_value)

                return getattr(instance.main, self.underlying_attr)

            def __set__(self, instance, value):
                setattr(instance.main, self.set_value_flag_attr, True)

                setattr(instance.main, self.underlying_attr, value)

            def __delete__(self, instance):
                delattr(instance.main, self.underlying_attr)

        def __init__(self, server, *, secrets, is_satellite, main=None, **kwargs):
            super().__init__(ctx=ServerboundPacket.Context(secrets), **kwargs)

            self.server = server

            self.is_satellite = is_satellite

            if is_satellite:
                self.main      = main
                self.satellite = self

                self.server.satellite_clients.append(self)
            else:
                # NOTE: The game sets both connections
                # to the main connection when constructing
                # a main connection object.
                self.main      = self
                self.satellite = self

                self.server.main_clients.append(self)

            self._keep_alive_lock = asyncio.Lock()
            self._keep_alive_task = None

            self._listen_sequentially = True

        async def _refresh_keep_alive(self):
            async with self._keep_alive_lock:
                if self._keep_alive_task is not None:
                    self._keep_alive_task.cancel()
                    await self._keep_alive_task

                self._keep_alive_task = asyncio.create_task(self.server._keep_alive_close(self))

        def close(self):
            try:
                if self.is_satellite:
                    self.server.satellite_clients.remove(self)
                else:
                    self.server.main_clients.remove(self)

            # We might already have been closed.
            except ValueError:
                pass

            if self._keep_alive_task is not None:
                self._keep_alive_task.cancel()

            super().close()

        async def wait_closed(self):

            if self._keep_alive_task is not None:
                await self._keep_alive_task

                self._keep_alive_task = None

            await super().wait_closed()

        @property
        def secrets(self):
            return self.ctx.secrets

        @secrets.setter
        def secrets(self, value):
            self.ctx = ServerboundPacket.Context(value)

        did_handshake = SynchronizedAttr(False)
        can_login     = SynchronizedAttr(False)
        logged_in     = SynchronizedAttr(False)

        auth_token         = SynchronizedAttr(0)
        verification_token = SynchronizedAttr(None)

        def client_verification_data(self):
            return self.secrets.client_verification_data(self.verification_token, ctx=self.ctx)

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

        async def _read_next_packet(self):
            length = await self._read_length()
            if length is None:
                return None

            # One extra byte for the fingerprint.
            data = await self.read_data(length + 1)
            if data is None:
                return None

            buf = io.BytesIO(data)

            header = ServerboundPacket.Header.unpack(buf, ctx=self.ctx)

            packet_cls = ServerboundPacket.subclass_with_id(header.id, ctx=self.ctx)
            if packet_cls is None:
                packet_cls = ServerboundPacket.GenericWithID(header.id)

            if self.secrets.packet_key_sources is not None:
                buf = packet_cls.decipher_data(buf, ctx=self.ctx, fingerprint=header.fingerprint)
            elif packet_cls.CIPHER is not None:
                packet_cls = ServerboundPacket.GenericWithID(header.id)

            return packet_cls.unpack_with_fingerprint(header.fingerprint, buf, ctx=self.ctx)

        async def write_packet_instance(self, packet):
            packet_data = packet.pack(ctx=self.ctx)

            type_ctx = pak.Type.Context(ctx=self.ctx)

            await self.write_data(
                types.VarInt.pack(len(packet_data), ctx=type_ctx) +

                packet_data
            )

            await self.server._listen_to_copied_packet(self, packet, outgoing=True)

    def __init__(
        self,
        *,
        host_main_address = None,
        host_main_port    = 11801,

        keep_alive_timeout = 60,

        loader_stage_size = None,

        version                      = None,
        auth_key                     = None,
        client_verification_template = None,
    ):
        super().__init__()

        self.host_main_address = host_main_address
        self.host_main_port    = host_main_port

        self.keep_alive_timeout = keep_alive_timeout

        self.loader_stage_size = loader_stage_size

        self.initial_secrets = Secrets(
            version                      = version,
            auth_key                     = auth_key,
            client_verification_template = client_verification_template,
        )

        self.main_srv     = None
        self.main_clients = []

        self.satellite_srv     = None
        self.satellite_clients = []

    def register_packet_listener(self, listener, *packet_types, outgoing=False, **flags):
        super().register_packet_listener(listener, *packet_types, outgoing=outgoing, **flags)

    def is_serving(self):
        return (
            (self.main_srv      is not None and self.main_srv.is_serving())      and
            (self.satellite_srv is     None or  self.satellite_srv.is_serving())
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

    async def _listen_to_copied_packet(self, client, packet, *, outgoing):
        listeners = self.listeners_for_packet(packet, outgoing=outgoing)
        if len(listeners) <= 0:
            return

        packet = packet.immutable_copy()

        async with self.listener_task_group(listen_sequentially=client._listen_sequentially) as group:
            for listener in listeners:
                group.create_task(listener(client, packet))

    async def _listen_to_incoming_packet(self, client, packet):
        async with self.listener_task_group(listen_sequentially=client._listen_sequentially) as group:
            for listener in self.listeners_for_packet(packet, outgoing=False):
                group.create_task(listener(client, packet))

    async def listen(self, client):
        while self.is_serving() and not client.is_closing():
            try:
                async for packet in client.continuously_read_packets():
                    # TODO: Should we abort the connection if
                    # the fingerprint is not correct? That is
                    # what the official server does.

                    packet.make_immutable()

                    await self._listen_to_incoming_packet(client, packet)

            finally:
                await self.end_listener_tasks()

    async def _keep_alive_close(self, client):
        # This will be canceled when a keep alive is received.

        try:
            await asyncio.sleep(self.keep_alive_timeout)

            client.close()
            await client.wait_closed()

        except asyncio.CancelledError:
            return

    async def new_main_connection(self, client_reader, client_writer):
        client = self.Connection(
            self,

            secrets      = self.initial_secrets,
            is_satellite = False,
            reader       = client_reader,
            writer       = client_writer,
        )

        async with client:
            if self.keep_alive_timeout is not None:
                await client._refresh_keep_alive()

            await self.listen(client)

    async def open_main_server(self):
        return await asyncio.start_server(self.new_main_connection, self.host_main_address, self.host_main_port)

    async def startup(self):
        self.main_srv = await self.open_main_server()

    async def on_start(self):
        await self.main_srv.serve_forever()

    async def start(self):
        await self.startup()

        async with self:
            await self.on_start()

    def run(self):
        try:
            asyncio.run(self.start())

        except KeyboardInterrupt:
            pass

    @property
    def version(self):
        return self.initial_secrets.version

    @version.setter
    def version(self, value):
        self.initial_secrets = self.initial_secrets.copy(version=value)

    @property
    def auth_key(self):
        return self.initial_secrets.auth_key

    @auth_key.setter
    def auth_key(self, value):
        self.initial_secrets = self.initial_secrets.copy(auth_key=value)

    @property
    def client_verification_template(self):
        return self.initial_secrets.client_verification_template

    @client_verification_template.setter
    def client_verification_template(self, value):
        self.initial_secrets = self.initial_secrets.copy(client_verification_template=value)

    @property
    def num_online_players(self):
        return sum(1 if x.logged_in else 0 for x in self.main_clients)

    def language_from_handshake(self, packet):
        return "en"

    def country_from_handshake(self, packet):
        return "us"

    async def on_login(self, client, packet):
        await client.write_packet(
            clientbound.AccountErrorPacket,

            error_code = 2,
        )

    @pak.packet_listener(serverbound.HandshakePacket)
    async def _on_handshake(self, client, packet):
        if self.loader_stage_size is not None and packet.loader_stage_size != self.loader_stage_size:
            client.close()
            await client.wait_closed()

            return

        if self.version is None:
            # NOTE: We only track what could matter.
            client.secrets = client.secrets.copy(version=packet.game_version)

        elif packet.game_version != self.version:
            client.close()
            await client.wait_closed()

            return

        client.did_handshake = True

        client.auth_token = random.randrange(self.MAX_AUTH_TOKEN + 1)

        await client.write_packet(
            clientbound.HandshakeResponsePacket,

            num_online_players = self.num_online_players,
            language           = self.language_from_handshake(packet),
            country            = self.country_from_handshake(packet),
            auth_token         = client.auth_token,
        )

        if self.client_verification_template is not None:
            client.verification_token = random.randrange(self.MAX_VERIFICATION_TOKEN + 1)

            await client.write_packet(
                clientbound.ClientVerificationPacket,

                verification_token = client.verification_token,
            )

    @pak.packet_listener(ServerboundPacket)
    async def _check_did_handshake(self, client, packet):
        # TODO: Should we really bother to care about this?

        if client.did_handshake or isinstance(packet, (serverbound.HandshakePacket, serverbound.ExtensionWrapperPacket)):
            return

        client.close()
        await client.wait_closed()

    @pak.packet_listener(serverbound.SetLanguagePacket)
    async def on_set_language(self, client, packet):
        # NOTE: Subclasses are encouraged to override this.

        await client.write_packet(
            clientbound.SetLanguagePacket,

            language = "en",
            country = "us",
        )

    @pak.packet_listener(serverbound.SystemInformationPacket)
    async def _on_system_information(self, client, packet):
        if self.client_verification_template is not None:
            return

        client.can_login = True

    @pak.packet_listener(serverbound.ClientVerificationPacket)
    async def _on_client_verification(self, client, packet):
        if packet.ciphered_data != self.secrets.client_verification_data(client.verification_token, ctx=ctx):
            client.close()
            await client.wait_closed()

            return

        client.can_login = True

    @pak.packet_listener(serverbound.LoginPacket)
    async def _on_login(self, client, packet):
        if not client.can_login:
            client.close()
            await client.wait_closed()

            return

        if self.auth_key is not None and packet.ciphered_auth_token != (client.auth_token ^ self.auth_key):
            client.close()
            await client.wait_closed()

            return

        await self.on_login(client, packet)

        if client.logged_in:
            client._listen_sequentially = False

    @pak.packet_listener(serverbound.KeepAlivePacket)
    async def _on_keep_alive(self, client, packet):
        if self.keep_alive_timeout is None:
            return

        await client._refresh_keep_alive()

    @pak.packet_listener(serverbound.TribulleWrapperPacket)
    async def _on_tribulle_wrapper(self, client, packet):
        await self._listen_to_copied_packet(client, packet.nested, outgoing=False)

    @pak.packet_listener(clientbound.TribulleWrapperPacket)
    async def _on_tribulle_wrapper_outgoing(self, client, packet):
        await self._listen_to_copied_packet(client, packet.nested, outgoing=True)

    @pak.packet_listener(serverbound.LegacyWrapperPacket)
    async def _on_legacy_wrapper(self, client, packet):
        await self._listen_to_copied_packet(client, packet.nested, outgoing=False)

    @pak.packet_listener(clientbound.LegacyWrapperPacket)
    async def _on_legacy_wrapper_outgoing(self, client, packet):
        await self._listen_to_copied_packet(client, packet.nested, outgoing=True)

    @pak.packet_listener(serverbound.ExtensionWrapperPacket)
    async def _on_extension_wrapper(self, client, packet):
        await self._listen_to_copied_packet(client, packet.nested, outgoing=False)

    @pak.packet_listener(clientbound.ExtensionWrapperPacket)
    async def _on_extension_wrapper_outgoing(self, client, packet):
        await self._listen_to_copied_packet(client, packet.nested, outgoing=True)

    @pak.packet_listener(serverbound.KeySourcesPacket)
    async def _load_packet_key_sources(self, client, packet):
        client.secrets = client.secrets.copy(packet_key_sources=packet.packet_key_sources)
