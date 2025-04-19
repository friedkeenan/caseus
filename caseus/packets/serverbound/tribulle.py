from public import public

from ..packet import ServerboundTribullePacket

from ... import types

@public
class TribeInvitePacket(ServerboundTribullePacket):
    id = 78

    target: types.String

@public
class AnswerTribeInvitePacket(ServerboundTribullePacket):
    id = 80

    inviter:  types.String
    accepted: types.ByteBoolean

@public
class CreateTribePacket(ServerboundTribullePacket):
    id = 84

    tribe_name: types.String

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

@public
class ChangeTribeMemberRankPacket(ServerboundTribullePacket):
    id = 112

    target:     types.String
    rank_index: types.Byte
