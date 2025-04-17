from public import public

from ..packet import ServerboundTribullePacket

from ... import types

@public
class ChangeTribeHouseMapPacket(ServerboundTribullePacket):
    id = 102

    map_code: types.Int

@public
class OpenTribeMenuPacket(ServerboundTribullePacket):
    id = 108

    include_disconnected_members: types.ByteBoolean

@public
class CloseTribeMenuPacket(ServerboundTribullePacket):
    id = 110
