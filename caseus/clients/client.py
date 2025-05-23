import asyncio
import io
import random
import fixedint
import pak

from public import public

from ..packets import (
    ClientboundPacket,
    serverbound,
    clientbound,
)

from .. import enums
from .. import types

@public
class AccountError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code

        super().__init__(f"Error code: '{error_code}'")

@public
class Client(pak.AsyncPacketHandler):
    # NOTE: By default, we act like a Windows standalone client.
    # These values are directly taken from such.

    PLAYER_TYPE         = "Éxécutable AIR"
    BROWSER_INFO        = "-"
    LOADER_SIZE         = 0x1FBD
    FONTS_HASH          = "223eaaa7e11bf4cd2e7953ed079527de3d5f4fbbf635260ed76c563214da9eeb"
    SERVER_STRING       = (
        "A=t&SA=t&SV=t&EV=t&MP3=t&AE=t&VE=t&ACC=t&PR=t&SP=f&SB=f&DEB=t&V=WIN 50,1,1,2&"
        "M=Adobe Windows&R=1920x1080&COL=color&AR=1.0&OS=Windows 10&ARCH=x86&L=en&IME=f&"
        "PR32=t&PR64=t&CAS=32&LS=en-US&PT=Desktop&AVD=f&LFD=f&WD=f&TLS=t&ML=5.1&DP=72"
    )
    REFERRER            = enums.Referrer.Unknown
    TIME_TILL_HANDSHAKE = 6884
    OS                  = "Windows 10"
    FLASH_VERSION       = "WIN 50,1,1,2"
    LOADER_URL          = "app:/TransformiceAIR.swf/[[DYNAMIC]]/2/[[DYNAMIC]]/4"

    class Connection(pak.io.Connection):
        def __init__(self, client, **kwargs):
            super().__init__(ctx=ClientboundPacket.Context(client.secrets), **kwargs)

            self.client = client

            self.fingerprint = random.randrange(0, 90)

        async def _read_length(self):
            type_ctx = pak.Type.Context(ctx=self.ctx)

            try:
                return await types.PacketLength.unpack_async(self.reader, ctx=type_ctx)
            except asyncio.IncompleteReadError:
                return None

        async def _read_next_packet(self):
            length = await self._read_length()
            if length is None:
                return None

            data = await self.read_data(length)
            if data is None:
                return None

            buf = io.BytesIO(data)

            header = ClientboundPacket.Header.unpack(buf, ctx=self.ctx)

            packet_cls = ClientboundPacket.subclass_with_id(header.id, ctx=self.ctx)
            if packet_cls is None:
                packet_cls = ClientboundPacket.GenericWithID(header.id)

            return packet_cls.unpack(buf, ctx=self.ctx)

        async def write_packet_instance(self, packet):
            header = packet.Header(fingerprint=self.fingerprint, id=packet.id(ctx=self.ctx))

            self.fingerprint = (self.fingerprint + 1) % 100

            packet_body = packet.pack_without_header(ctx=self.ctx)
            packet_body = packet.cipher_data(packet_body, ctx=self.ctx, fingerprint=header.fingerprint)

            packet_data = header.pack(ctx=self.ctx) + packet_body

            await self.write_data(
                types.PacketLength.pack(
                    len(packet_data) - 1,

                    ctx = pak.Type.Context(ctx=self.ctx)
                ) +

                packet_data
            )

            await self.client._listen_to_packet_with_fingerprint(self, packet, fingerprint=header.fingerprint)

    def __init__(
        self,
        *,
        secrets,

        username,
        password_hash,
        start_room,

        system_language  = "en",
        desired_language = None,

        steam_id = None,

        connect_to_satellite = True,

        listen_sequentially = False,
    ):
        super().__init__()

        self.secrets = secrets

        self.username      = username
        self.password_hash = password_hash
        self.start_room    = start_room

        self.auth_token = 0
        self.session_id = None

        self.system_language  = system_language
        self.desired_language = desired_language

        if isinstance(steam_id, int):
            steam_id = str(steam_id)

        self.steam_id = steam_id

        if connect_to_satellite:
            self.register_packet_listener(self._on_change_satellite_server, clientbound.ChangeSatelliteServerPacket)

        # TODO: Should we also set this to '0'
        # if the client starts up again?
        self._tribulle_fingerprint = fixedint.Int32(0)

        self.listen_sequentially  = listen_sequentially
        self._listen_sequentially = True

    def is_bot_role(self):
        return self.secrets.is_bot_role()

    def register_packet_listener(self, listener, *packet_types, outgoing=False, **fields):
        super().register_packet_listener(listener, *packet_types, outgoing=outgoing, **fields)

    async def _listen_to_packet_with_fingerprint(self, server, packet, *, fingerprint):
        # For listeners that are listening to written packets,
        # the fingerprint may be important to them, and so we
        # make a copy of the packet with the fingerprint set
        # for them to listen to if there are any listeners.

        # NOTE: All fingerprinted packets are outgoing.
        listeners = self.listeners_for_packet(packet, outgoing=True)
        if len(listeners) <= 0:
            return

        packet = packet.immutable_copy(fingerprint=fingerprint)

        async with self.listener_task_group(listen_sequentially=self._listen_sequentially) as group:
            for listener in listeners:
                group.create_task(listener(server, packet))

    async def _listen_to_packet(self, server, packet, *, outgoing):
        async with self.listener_task_group(listen_sequentially=self._listen_sequentially) as group:
            for listener in self.listeners_for_packet(packet, outgoing=outgoing):
                # NOTE: The game does not track what connection
                # a packet came from, and so almost all packet
                # listeners should simply ignore the passed
                # connection. However some listeners will need
                # to know what connection a packet came from,
                # and as a matter of principle it would be
                # unfortunate to throw away such information.
                group.create_task(listener(server, packet))

    async def listen(self, server):
        try:
            async for packet in server.continuously_read_packets():
                packet.make_immutable()

                await self._listen_to_packet(server, packet, outgoing=False)

        finally:
            await self.end_listener_tasks()

    def _advance_tribulle_fingerprint(self):
        self._tribulle_fingerprint += 1

        return int(self._tribulle_fingerprint)

    async def write_tribulle(self, packet_cls, /, **fields):
        await self.main.write_packet(
            serverbound.TribulleWrapperPacket,

            nested = self.main.create_packet(
                packet_cls,

                fingerprint = self._advance_tribulle_fingerprint(),

                **fields,
            ),
        )

        return self._tribulle_fingerprint

    async def write_tribulle_instance(self, packet):
        await self.main.write_packet(
            serverbound.TribulleWrapperPacket,

            nested = packet.copy(fingerprint=self._advance_tribulle_fingerprint())
        )

        return self._tribulle_fingerprint

    async def open_streams(self, address, ports):
        for port in random.sample(ports, len(ports)):
            try:
                return await asyncio.open_connection(address, port)

            except Exception:
                continue

        raise ValueError(f"Unable to connect to address '{address}' on ports {ports}")

    async def startup(self):
        reader, writer = await self.open_streams(self.secrets.server_address, self.secrets.server_ports)

        self.main = self.Connection(self, reader=reader, writer=writer)

        # We set our satellite connection to our main connection
        # just like the game does until it is told to change the
        # satellite server.
        self.satellite = self.main

    async def _keep_alive(self):
        # NOTE: The client normally checks whether the player has done
        # nothing for 6 hours and ends the connection if so, with some
        # exceptions like for being in a tribe house map. We neglect to
        # do so here.

        try:
            # TODO: Should we check satellite here too?
            while not self.main.is_closing():
                # NOTE: The game sends the keep alive packets
                # 15 seconds after sending the handshake packet,
                # and then repeats every 15 seconds after that.
                # To mimic this, we sleep 15 seconds at the start
                # of each loop.
                await asyncio.sleep(15)

                await self.main.write_packet(serverbound.KeepAlivePacket)
                await self.satellite.write_packet(serverbound.KeepAlivePacket)

        except asyncio.CancelledError:
            return

    async def _satellite_listen(self):
        try:
            while not self.main.is_closing():
                if self.satellite is self.main or self.satellite.is_closing():
                    await pak.util.yield_exec()

                    continue

                async with self.satellite:
                    await self.listen(self.satellite)

        except asyncio.CancelledError:
            return

    async def handshake(self):
        language = self.system_language
        if language == "nb":
            # The game changes the language from 'Capabilities'
            # to 'no' if it has the value 'nb', corresponding
            # to Norwegian.
            language = "no"

        await self.main.write_packet(
            serverbound.HandshakePacket,

            game_version                = self.secrets.game_version,
            language                    = language,
            connection_token            = self.secrets.connection_token,
            player_type                 = self.PLAYER_TYPE,
            browser_info                = self.BROWSER_INFO,
            loader_stage_size           = self.LOADER_SIZE,
            concatenated_font_name_hash = self.FONTS_HASH,
            server_string               = self.SERVER_STRING,
            referrer                    = self.REFERRER,
            milliseconds_since_start    = self.TIME_TILL_HANDSHAKE,
        )

    async def login(self):
        if self.secrets.auth_key is not None:
            ciphered_auth_token = self.auth_token ^ self.secrets.auth_key
        else:
            ciphered_auth_token = None

        await self.main.write_packet(
            serverbound.LoginPacket,

            username            = self.username,
            password_hash       = self.password_hash,
            loader_url          = self.LOADER_URL,
            start_room          = self.start_room,
            ciphered_auth_token = ciphered_auth_token,
            unk_short_6         = 18,
        )

    async def on_start(self):
        await self.handshake()

        keep_alive_task       = asyncio.create_task(self._keep_alive())
        satellite_listen_task = asyncio.create_task(self._satellite_listen())

        try:
            await self.listen(self.main)

        finally:
            satellite_listen_task.cancel()
            keep_alive_task.cancel()

            await satellite_listen_task
            await keep_alive_task

    async def start(self):
        await self.startup()

        async with self.main:
            await self.on_start()

    def run(self):
        try:
            asyncio.run(self.start())

        except KeyboardInterrupt:
            pass

    async def set_desired_language(self, *, fallback):
        if self.desired_language is None:
            language = fallback
        else:
            language = self.desired_language

        await self.main.write_packet(
            serverbound.SetLanguagePacket,

            language = language,
        )

    @pak.packet_listener(clientbound.HandshakeResponsePacket)
    async def _on_handshake_response(self, server, packet):
        self.auth_token = packet.auth_token

        # The game may send a language stored in
        # its shared data, but if that is not
        # possible then it falls back to the one
        # in the received packet.
        await self.set_desired_language(fallback=packet.language)

        await self.main.write_packet(
            serverbound.SystemInformationPacket,

            # The game uses the language from the 'Capabilities' class.
            language      = self.system_language,
            os            = self.OS,
            flash_version = self.FLASH_VERSION,
        )

        if self.steam_id is not None:
            await self.main.write_packet(
                serverbound.SteamInfoPacket,

                user_id = self.steam_id,
            )

    @pak.packet_listener(clientbound.ClientVerificationPacket)
    async def _on_client_verification(self, server, packet):
        # NOTE: Bot role clients still receive this packet.

        if self.secrets.client_verification_template is not None:
            await self.main.write_packet(
                serverbound.ClientVerificationPacket,

                ciphered_data = self.secrets.client_verification_data(
                    packet.verification_token,

                    ctx = self.main.ctx,
                )
            )

        # NOTE: We allow not logging in by just
        # supplying 'None' as the username, if
        # for some reason someone wants to do the
        # equivalent of sitting at the login screen.
        if self.username is not None:
            await self.login()

    @pak.packet_listener(clientbound.AccountErrorPacket)
    async def _on_account_error(self, server, packet):
        raise AccountError(packet.error_code)

    @pak.packet_listener(clientbound.LoginSuccessPacket)
    async def _on_login_success(self, server, packet):
        # TODO: Does it make sense for this class to track this?
        self.session_id = packet.session_id

        if not self.listen_sequentially:
            self._listen_sequentially = False

    async def _on_change_satellite_server(self, server, packet):
        if packet.should_ignore:
            return

        if self.satellite is not self.main:
            self.satellite.close()
            await self.satellite.wait_closed()

        reader, writer = await self.open_streams(packet.address, packet.ports)
        self.satellite = self.Connection(self, reader=reader, writer=writer)

        # NOTE: The game delays sending this packet until it
        # otherwise tries to send a packet to the satellite
        # server. We do not do this and instead send it right away.
        await self.satellite.write_packet(
            serverbound.SatelliteDelayedIdentificationPacket,

            timestamp = packet.timestamp,
            global_id = packet.global_id,
            auth_id   = packet.auth_id,
        )

    @pak.packet_listener(clientbound.PingPacket)
    async def _on_ping(self, server, packet):
        if packet.main_server:
            await self.main.write_packet(
                serverbound.PongPacket,

                payload = packet.payload,
            )

        else:
            await self.satellite.write_packet(
                serverbound.PongPacket,

                payload = packet.payload,
            )

    # Listen to nested packets.

    @pak.packet_listener(clientbound.TribulleWrapperPacket)
    async def _on_tribulle_wrapper(self, server, packet):
        await self._listen_to_packet(server, packet.nested.immutable_copy(), outgoing=False)

    @pak.packet_listener(serverbound.TribulleWrapperPacket, outgoing=True)
    async def _on_tribulle_wrapper_outgoing(self, server, packet):
        await self._listen_to_packet(server, packet.nested.immutable_copy(), outgoing=True)

    @pak.packet_listener(clientbound.LegacyWrapperPacket)
    async def _on_legacy_wrapper(self, server, packet):
        await self._listen_to_packet(server, packet.nested.immutable_copy(), outgoing=False)

    @pak.packet_listener(serverbound.LegacyWrapperPacket, outgoing=True)
    async def _on_legacy_wrapper_outgoing(self, server, packet):
        await self._listen_to_packet(server, packet.nested.immutable_copy(), outgoing=True)

    @pak.packet_listener(clientbound.ExtensionWrapperPacket)
    async def _on_extension_wrapper(self, server, packet):
        await self._listen_to_packet(server, packet.nested.immutable_copy(), outgoing=False)

    @pak.packet_listener(serverbound.ExtensionWrapperPacket, outgoing=True)
    async def _on_extension_wrapper_outgoing(self, server, packet):
        await self._listen_to_packet(server, packet.nested.immutable_copy(), outgoing=True)
