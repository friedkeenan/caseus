import pak

from public import public

from .proxy import Proxy

from ..packets import serverbound, clientbound

@public
class InputListeningProxy(Proxy):
    class ServerConnection(Proxy.ServerConnection):
        @property
        def _mouse_info(self):
            return self.main.client._main_mouse_info

        @property
        def _key_info(self):
            return self.main.client._main_key_info

        async def listen_to_mouse(self, listen=True):
            await source.destination.listen_to_mouse(listen)

        async def listen_to_keyboard(self, key_codes, listen=True, *, down=True):
            await self.destination.listen_to_keyboard(key_codes, listen, down=down)

    class ClientConnection(Proxy.ClientConnection):
        class _MouseListenerInfo:
            def __init__(self):
                self.proxy_listening = False
                self.game_listening  = False

        class _KeyListenerInfo:
            def __init__(self):
                self._game_listeners  = [set(), set()]
                self._proxy_listeners = [set(), set()]

            def reset_game_listeners(self):
                self._game_listeners[0].clear()
                self._game_listeners[1].clear()

            def game_listeners(self, *, down):
                return self._game_listeners[int(down)]

            def proxy_listeners(self, *, down):
                return self._proxy_listeners[int(down)]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if not self.is_satellite:
                self._main_mouse_info = self._MouseListenerInfo()
                self._main_key_info   = self._KeyListenerInfo()

        @property
        def _mouse_info(self):
            return self.main.client._main_mouse_info

        @property
        def _key_info(self):
            return self.main.client._main_key_info

        async def listen_to_mouse(self, listen=True):
            if not self._mouse_info.game_listening and listen is not self._mouse_info.proxy_listening:
                await self.write_packet(
                    clientbound.BindMouseDownPacket,

                    active = listen,
                )

            self._mouse_info.proxy_listening = listen

        async def listen_to_keyboard(self, key_codes, listen=True, *, down=True):
            if isinstance(key_codes, int):
                key_codes = (key_codes,)

            proxy_listeners = self._key_info.proxy_listeners(down=down)

            for key_code in key_codes:
                previously_listening = key_code in proxy_listeners

                if (
                    key_code not in self._key_info.game_listeners(down=down) and

                    listen is not previously_listening
                ):
                    await self.write_packet(
                        clientbound.BindKeyboardPacket,

                        key_code = key_code,
                        down     = down,
                        active   = listen,
                    )

                if listen:
                    proxy_listeners.add(key_code)
                else:
                    try:
                        proxy_listeners.remove(key_code)

                    except KeyError:
                        pass

    @pak.packet_listener(clientbound.BindMouseDownPacket)
    async def _track_mouse_game_listening(self, source, packet):
        source._mouse_info.game_listening = packet.active

    @pak.packet_listener(clientbound.BindKeyboardPacket)
    async def _track_key_game_listeners(self, source, packet):
        if packet.active:
            source._key_info.game_listeners(down=packet.down).add(packet.key_code)
        else:
            try:
                source._key_info.game_listeners(down=packet.down).remove(packet.key_code)
            except KeyError:
                pass

    # NOTE: The official server does not seem to care about unexpected
    # mouse down packets or keyboard packets, however we take care
    # here to nonetheless not forward on any packets the server would
    # not expect.

    @pak.packet_listener(serverbound.MouseDownPacket)
    async def _listen_to_mouse_down(self, source, packet):
        if source._mouse_info.proxy_listening:
            await self.on_mouse_down(source, packet)

        if not source._mouse_info.game_listening:
            return self.REPLACE_PACKET

        return self.FORWARD_PACKET

    @pak.packet_listener(serverbound.KeyboardPacket)
    async def _listen_to_keyboard(self, source, packet):
        if packet.key_code in source._key_info.proxy_listeners(down=packet.down):
            await self.on_keyboard(source, packet)

        if packet.key_code not in source._key_info.game_listeners(down=packet.down):
            return self.REPLACE_PACKET

        return self.FORWARD_PACKET

    async def _reenable_key_listeners(self, client, *, down):
        for key_code in client._key_info.proxy_listeners(down=down):
            await client.write_packet(
                clientbound.BindKeyboardPacket,

                key_code = key_code,
                down     = down,
                active   = True,
            )

    @pak.packet_listener(clientbound.CleanupLuaScriptingPacket, clientbound.JoinedRoomPacket, after=True)
    async def _reenable_input_listeners(self, source, packet):
        source._mouse_info.game_listening = False
        source._key_info.reset_game_listeners()

        if source._mouse_info.proxy_listening:
            await source.destination.write_packet(
                clientbound.BindMouseDownPacket,

                active = True,
            )

        await self._reenable_key_listeners(source.destination, down=True)
        await self._reenable_key_listeners(source.destination, down=False)

    async def on_mouse_down(self, client, packet):
        raise NotImplementedError

    async def on_keyboard(self, client, packet):
        raise NotImplementedError
