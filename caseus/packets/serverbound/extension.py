from public import public

from ..packet import ServerboundExtensionPacket

from ... import types

@public
class KeySourcesPacket(ServerboundExtensionPacket):
    id = "packet_key_sources"

    packet_key_sources: types.UnsignedByte[None]
