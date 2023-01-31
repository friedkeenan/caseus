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

    class ClientConnection(Proxy.ClientConnection):
        class _MouseListenerInfo:
            def __init__(self):
                self.proxy_listening = True
                self.game_listening  = True

        class _KeyListenerInfo:
            def __init__(self):
                self._game_listeners = {
                    True:  set(),
                    False: set(),
                }

                self._proxy_listeners = {
                    True:  set(),
                    False: set(),
                }

            def reset_game_listeners(self):
                self._game_listeners[True].clear()
                self._game_listeners[False].clear()

            def game_listeners(self, *, down):
                return self._game_listeners[down]

            def proxy_listeners(self, *, down):
                return self._proxy_listeners[down]

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
                    clientbound.SetSendMouseDownPacket,

                    enable = listen,
                )

            self._mouse_info.proxy_listening = listen

        async def listen_to_keyboard(self, key_code, listen=True, *, down=True):
            proxy_listeners = self._key_info.proxy_listeners(down=down)

            previously_listening = key_code in proxy_listeners

            if (
                key_code not in self._key_info.game_listeners(down=down) and

                listen is not previously_listening
            ):
                await self.write_packet(
                    clientbound.SetSendKeyboardPacket,

                    key_code = key_code,
                    down     = down,
                    enable   = listen,
                )

            if listen:
                proxy_listeners.add(key_code)
            else:
                proxy_listeners.remove(key_code)

    @pak.packet_listener(clientbound.SetSendMouseDownPacket)
    async def _track_mouse_game_listening(self, source, packet):
        source._mouse_info.game_listening = packet.enable

    @pak.packet_listener(clientbound.SetSendKeyboardPacket)
    async def _track_key_game_listeners(self, source, packet):
        if packet.enable:
            source._key_info.game_listeners(down=packet.down).add(packet.key_code)
        else:
            try:
                source._key_info.game_listeners(down=packet.down).remove(packet.key_code)
            except KeyError:
                pass

    # NOTE: The game server does not seem to care about unexpected
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
                clientbound.SetSendKeyboardPacket,

                key_code = key_code,
                down     = down,
                enable   = True,
            )

    @pak.packet_listener(clientbound.CleanupLuaScriptingPacket, clientbound.JoinedRoomPacket, after=True)
    async def _reenable_input_listeners(self, source, packet):
        source._mouse_info.game_listening = False
        source._key_info.reset_game_listeners()

        if source._mouse_info.proxy_listening:
            await source.destination.write_packet(
                clientbound.SetSendMouseDownPacket,

                enable = True,
            )

        await self._reenable_key_listeners(source.destination, down=True)
        await self._reenable_key_listeners(source.destination, down=False)

    async def on_mouse_down(self, client, packet):
        raise NotImplementedError

    async def on_keyboard(self, client, packet):
        raise NotImplementedError
