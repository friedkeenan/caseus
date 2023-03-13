import pak

from public import public

from .client import Client

from ..packets import clientbound, serverbound

@public
class EnterTribeHouseClient(Client):
    @pak.packet_listener(clientbound.ConnectedToCommunityPlatformPacket)
    async def _enter_tribe_house(self, server, packet):
        await self.main.write_packet(serverbound.EnterTribeHousePacket)
