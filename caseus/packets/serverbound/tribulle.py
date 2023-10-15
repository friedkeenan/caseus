from public import public

from ..packet import ServerboundTribullePacket

from ... import types

@public
class ChangeTribeHouseMapPacket(ServerboundTribullePacket):
    id = 102

    map_code: types.Int
