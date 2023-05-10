import pak

from public import public

from aioconsole import aprint

from .sniffer import Sniffer

from ..packets import Packet, ServerboundPacket

@public
class LoggingSniffer(Sniffer):
    LOG_GENERIC_PACKETS = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.LOG_GENERIC_PACKETS:
            self.register_packet_listener(self._log_packet, Packet)
        else:
            self.register_packet_listener(self._log_specific_packets, Packet)

    async def _log_packet(self, server, packet):
        if isinstance(packet, ServerboundPacket):
            bound = "Serverbound"
        else:
            bound = "Clientbound"

        await aprint(f"{server.name}: {bound}: {packet}")

    async def _log_specific_packets(self, server, packet):
        if isinstance(packet, pak.GenericPacket):
            return

        await self._log_packet(server, packet)
