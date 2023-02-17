import pak

from aioconsole import aprint

from public import public

from .client import Client

from ..packets import Packet, GenericPacket

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

    async def _log_packet(self, conn, packet, *, bound):
        # NOTE: It is important that we check
        # the main connection first, as at the
        # start of the client process, the
        # satellite connection is the main connection.
        if conn is self.main:
            connection_name = "MAIN"
        else:
            connection_name = "SATELLITE"

        await aprint(f"{connection_name}: {bound}: {packet}")

    async def _log_all_incoming_packets(self, conn, packet):
        await self._log_packet(conn, packet, bound="Clientbound")

    async def _log_specific_incoming_packets(self, conn, packet):
        if isinstance(packet, GenericPacket):
            return

        await self._log_packet(conn, packet, bound="Clientbound")

    async def _log_all_outgoing_packets(self, conn, packet):
        await self._log_packet(conn, packet, bound="Serverbound")

    async def _log_specific_outgoing_packets(self, conn, packet):
        if isinstance(packet, GenericPacket):
            return

        await self._log_packet(conn, packet, bound="Serverbound")
