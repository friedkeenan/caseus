from aioconsole import aprint

from public import public

from .server import MinimalServer

from ..packets import Packet

@public
class LoggingServer(MinimalServer):
    LOG_GENERIC_PACKETS  = True
    LOG_OUTGOING_PACKETS = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.LOG_GENERIC_PACKETS:
            self.register_packet_listener(self._log_all_incoming_packets, Packet)

            if self.LOG_OUTGOING_PACKETS:
                self.register_packet_listener(self._log_all_outgoing_packets, Packet, outgoing=True)

        else:
            self.register_packet_listener(self._log_specific_incoming_packets, Packet)

            if self.LOG_OUTGOING_PACKETS:
                self.register_packet_listener(self._log_specific_outgoing_packets, Packet, outgoing=True)

    async def _log_packet(self, client, packet, *, bound):
        if client.is_satellite:
            connection_name = "SATELLITE"
        else:
            connection_name = "MAIN"

        await aprint(f"{connection_name}: {bound}: {packet}")

    async def _log_all_incoming_packets(self, client, packet):
        await self._log_packet(client, packet, bound="Serverbound")

    async def _log_specific_incoming_packets(self, client, packet):
        if isinstance(packet, pak.GenericPacket):
            return

        await self._log_packet(client, packet, bound="Serverbound")

    async def _log_all_outgoing_packets(self, client, packet):
        await self._log_packet(client, packet, bound="Clientbound")

    async def _log_specific_outgoing_packets(self, client, packet):
        if isinstance(packet, pak.GenericPacket):
            return

        await self._log_packet(client, packet, bound="Clientbound")
