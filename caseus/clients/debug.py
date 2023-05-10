import pak

from aioconsole import aprint

from public import public

from .client import Client

from ..packets import Packet

@public
class LoggingClient(Client):
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

    async def _log_packet(self, server, packet, *, bound):
        # NOTE: It is important that we check
        # the main connection first, as at the
        # start of the client process, the
        # satellite connection is the main connection.
        if server is self.main:
            connection_name = "MAIN"
        else:
            connection_name = "SATELLITE"

        await aprint(f"{connection_name}: {bound}: {packet}")

    async def _log_all_incoming_packets(self, server, packet):
        await self._log_packet(server, packet, bound="Clientbound")

    async def _log_specific_incoming_packets(self, server, packet):
        if isinstance(packet, pak.GenericPacket):
            return

        await self._log_packet(server, packet, bound="Clientbound")

    async def _log_all_outgoing_packets(self, server, packet):
        await self._log_packet(server, packet, bound="Serverbound")

    async def _log_specific_outgoing_packets(self, server, packet):
        if isinstance(packet, pak.GenericPacket):
            return

        await self._log_packet(server, packet, bound="Serverbound")
