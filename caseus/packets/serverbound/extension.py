from public import public

from ..packet import ServerboundExtensionPacket

from ... import types

@public
class KeySourcesPacket(ServerboundExtensionPacket):
    id = "packet_key_sources"

    packet_key_sources: types.UnsignedByte[None]

@public
class MainServerInfoPacket(ServerboundExtensionPacket):
    id = "main_server_info"

    address: types.String
    ports:   types.UnsignedShort[None]
