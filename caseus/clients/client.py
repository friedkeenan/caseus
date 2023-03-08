import asyncio
import io
import random
import pak

from public import public

from ..packets import (
    ClientboundPacket,
    GenericPacketWithID,
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
    MAIN_SERVER_PORTS = [11801, 12801, 13801, 14801]

    # NOTE: By default, we act like a Steam client.
    # These values are directly taken from such.

    PLAYER_TYPE         = "Steam AIR"
    BROWSER_INFO        = "-"
    LOADER_SIZE         = 0x7EE88
    FONTS_HASH          = "5610fd5713a0ed29fb13b576d2e0e4692dd99ddbbcd7b5c0a32b7271c91083e0"
    SERVER_STRING       = (
        "A=t&SA=t&SV=t&EV=t&MP3=t&AE=t&VE=t&ACC=t&PR=t&SP=f&SB=f&DEB=f&V=WIN 16,0,0,276&"
        "M=Adobe Windows&R=1920x1080&COL=color&AR=1.0&OS=Windows 8&ARCH=x86&L=en&IME=f&"
        "PR32=t&PR64=t&LS=en-US&PT=Desktop&AVD=f&LFD=f&WD=f&TLS=t&ML=5.1&DP=72"
    )
    REFEREE             = enums.RefereeID.Steam
    TIME_TILL_HANDSHAKE = 3128
    OS                  = "Windows 8"
    FLASH_VERSION       = "WIN 16,0,0,276"
    LOADER_URL          = "app:/Transformice.swf/[[DYNAMIC]]/1"

    class Connection(pak.io.Connection):
        def __init__(self, client, **kwargs):
            super().__init__(ctx=ClientboundPacket.Context(client.secrets), **kwargs)

            self.client = client

            self.fingerprint = random.randrange(0, 90)

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
                packet_cls = GenericPacketWithID(header.id, ClientboundPacket)

            return packet_cls.unpack(buf, ctx=self.ctx)

        async def write_packet_instance(self, packet):
            header = packet.Header(fingerprint=self.fingerprint, id=packet.id(ctx=self.ctx))

            self.fingerprint = (self.fingerprint + 1) % 100

            packet_body = packet.pack_without_header(ctx=self.ctx)
            packet_body = packet.cipher_data(packet_body, ctx=self.ctx, fingerprint=header.fingerprint)

            packet_data = header.pack(ctx=self.ctx) + packet_body

            await self.write_data(
                types.VarInt.pack(
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

        language = "en",
        steam_id = None,

        listen_sequentially = False,
    ):
        super().__init__()

        self.secrets = secrets

        self.username      = username
        self.password_hash = password_hash
        self.start_room    = start_room

        self.auth_token = 0
        self.session_id = None

        self.language = language

        if isinstance(steam_id, int):
            steam_id = str(steam_id)

        self.steam_id = steam_id

        self.listen_sequentially  = listen_sequentially
        self._listen_sequentially = True

    def register_packet_listener(self, listener, *packet_types, outgoing=False, **fields):
        super().register_packet_listener(listener, *packet_types, outgoing=outgoing, **fields)

    async def _listen_to_packet_with_fingerprint(self, conn, packet, *, fingerprint):
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
                group.create_task(listener(conn, packet))

    async def _listen_to_packet(self, conn, packet, *, outgoing):
        async with self.listener_task_group(listen_sequentially=self._listen_sequentially) as group:
            for listener in self.listeners_for_packet(packet, outgoing=outgoing):
                # NOTE: The game does not track what connection
                # a packet came from, and so almost all packet
                # listeners should simply ignore the passed
                # connection. However some listeners will need
                # to know what connection a packet came from,
                # and as a matter of principle it would be
                # unfortunate to throw away such information.
                group.create_task(listener(conn, packet))

    async def listen(self, conn):
        try:
            async for packet in conn.continuously_read_packets():
                packet.make_immutable()

                await self._listen_to_packet(conn, packet, outgoing=False)

        finally:
            await self.end_listener_tasks()

    async def open_streams(self, address, ports):
        for port in random.sample(ports, len(ports)):
            try:
                return await asyncio.open_connection(address, port)

            except Exception:
                continue

        raise ValueError(f"Unable to connect to address '{address}' on ports {ports}")

    async def startup(self):
        reader, writer = await self.open_streams(self.secrets.server_address, self.MAIN_SERVER_PORTS)

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

    async def on_start(self):
        language = self.language
        if language == "nb":
            # The game changes the language from 'Capabilities'
            # to 'no' if it has the value 'nb', corresponding
            # to Norwegian.
            language = "no"

        await self.main.write_packet(
            serverbound.HandshakePacket,

            game_version                = self.secrets.version,
            language                    = language,
            connection_token            = self.secrets.connection_token,
            player_type                 = self.PLAYER_TYPE,
            browser_info                = self.BROWSER_INFO,
            loader_stage_size           = self.LOADER_SIZE,
            concatenated_font_name_hash = self.FONTS_HASH,
            server_string               = self.SERVER_STRING,
            referee                     = self.REFEREE,
            milliseconds_since_start    = self.TIME_TILL_HANDSHAKE,
        )

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

    @pak.packet_listener(clientbound.HandshakeResponsePacket)
    async def _on_handshake_response(self, conn, packet):
        self.auth_token = packet.auth_token

        await self.main.write_packet(
            serverbound.SetLanguagePacket,

            # The game may send a language stored in
            # its shared data, but if that is not
            # possible then it falls back to the one
            # in the received packet.
            language = packet.language,
        )

        await self.main.write_packet(
            serverbound.SystemInformationPacket,

            # The game uses the language from the 'Capabilities' class.
            language      = self.language,
            os            = self.OS,
            flash_version = self.FLASH_VERSION,
        )

        if self.steam_id is not None:
            await self.main.write_packet(
                serverbound.SteamInfoPacket,

                user_id = self.steam_id,
            )

    @pak.packet_listener(clientbound.ClientVerificationPacket)
    async def _on_client_verification(self, conn, packet):
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
            await self.main.write_packet(
                serverbound.LoginPacket,

                username            = self.username,
                password_hash       = self.password_hash,
                loader_url          = self.LOADER_URL,
                start_room          = self.start_room,
                ciphered_auth_token = self.auth_token ^ self.secrets.auth_key,
                unk_short_6         = 18,
            )

    @pak.packet_listener(clientbound.AccountErrorPacket)
    async def _on_account_error(self, conn, packet):
        raise AccountError(packet.error_code)

    @pak.packet_listener(clientbound.LoginSuccessPacket)
    async def _on_login_success(self, conn, packet):
        # TODO: Does it make sense for this class to track this?
        self.session_id = packet.session_id

        if not self.listen_sequentially:
            self._listen_sequentially = False

    @pak.packet_listener(clientbound.ChangeSatelliteServerPacket)
    async def _on_change_satellite_server(self, conn, packet):
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
    async def _on_ping(self, conn, packet):
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
    async def _on_tribulle_wrapper(self, conn, packet):
        await self._listen_to_packet(conn, packet.nested.immutable_copy(), outgoing=False)

    @pak.packet_listener(serverbound.TribulleWrapperPacket, outgoing=True)
    async def _on_tribulle_wrapper_outgoing(self, conn, packet):
        await self._listen_to_packet(conn, packet.nested.immutable_copy(), outgoing=True)

    @pak.packet_listener(clientbound.LegacyWrapperPacket)
    async def _on_legacy_wrapper(self, conn, packet):
        await self._listen_to_packet(conn, packet.nested.immutable_copy(), outgoing=False)

    @pak.packet_listener(serverbound.LegacyWrapperPacket, outgoing=True)
    async def _on_legacy_wrapper_outgoing(self, conn, packet):
        await self._listen_to_packet(conn, packet.nested.immutable_copy(), outgoing=True)

    @pak.packet_listener(clientbound.ExtensionWrapperPacket)
    async def _on_extension_wrapper(self, conn, packet):
        await self._listen_to_packet(conn, packet.nested.immutable_copy(), outgoing=False)

    @pak.packet_listener(serverbound.ExtensionWrapperPacket, outgoing=True)
    async def _on_extension_wrapper_outgoing(self, conn, packet):
        await self._listen_to_packet(conn, packet.nested.immutable_copy(), outgoing=True)
