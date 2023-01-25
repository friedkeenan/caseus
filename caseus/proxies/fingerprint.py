import random

from public import public

from .proxy import Proxy

from ..packets import ServerboundPacket

@public
class FingerprintHandlingProxy(Proxy):
    # NOTE: This will send bogus data for serverbound packets
    # whose cipher depends on their fingerprint, i.e. ones with
    # the XOR cipher, if they are not also identified properly by
    # the library. It would not be hard to identify all of these
    # XOR-ciphered packets, but currently that has not been done.

    class ServerConnection(Proxy.ServerConnection):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fingerprint = random.randrange(90)

        def _written_packet_data(self, packet):
            header = ServerboundPacket.Header(
                fingerprint = self.fingerprint,
                id          = packet.id(ctx=self.ctx),
            )

            self.fingerprint = (self.fingerprint + 1) % 100

            packet_body = packet.pack_without_header(ctx=self.ctx)
            packet_body = packet.cipher_data(packet_body, secrets=self.secrets, fingerprint=header.fingerprint)

            return header.pack(ctx=self.ctx) + packet_body
