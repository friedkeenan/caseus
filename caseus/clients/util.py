import asyncio
import pak

from public import public

from .client import Client

from ..packets import clientbound, serverbound

@public
class EnterTribeHouseClient(Client):
    DELAY_TO_ENTER_TRIBE_HOUSE = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._login_time = None

    @pak.packet_listener(clientbound.LoginSuccessPacket)
    async def _track_login_time(self, server, packet):
        self._login_time = asyncio.get_running_loop().time()

    @pak.packet_listener(clientbound.ConnectedToCommunityPlatformPacket)
    async def _enter_tribe_house(self, server, packet):
        if self._login_time is None:
            await asyncio.sleep(self.DELAY_TO_ENTER_TRIBE_HOUSE)
        else:
            time_since_login = asyncio.get_running_loop().time() - self._login_time

            if time_since_login < self.DELAY_TO_ENTER_TRIBE_HOUSE:
                await asyncio.sleep(self.DELAY_TO_ENTER_TRIBE_HOUSE - time_since_login)

        await self.main.write_packet(serverbound.EnterTribeHousePacket)
