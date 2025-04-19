import pak

from public import public

from ..packet import ClientboundTribullePacket, FingerprintedClientboundTribullePacket
from ..common import TribeMemberInfo, TribeRankInfo
from ... import types
from ... import enums

@public
class ConnectedToCommunityPlatformPacket(ClientboundTribullePacket):
    id = 3

    class FriendInfo(pak.SubPacket):
        global_id:     types.Int
        username:      types.SignedLengthString
        gender:        pak.Enum(types.Byte, enums.Gender)
        avatar_id:     types.Int
        bidirectional: types.ByteBoolean
        connected:     types.ByteBoolean
        game_id:       types.Int
        room_name:     types.SignedLengthString
        last_login:    types.Int

    gender:    pak.Enum(types.Byte, enums.Gender)
    global_id: types.Int

    soulmate:  FriendInfo
    friends:   FriendInfo[types.Short]
    blacklist: types.SignedLengthString[types.Short]

    tribe_name:     types.SignedLengthString
    tribe_id:       types.Int
    greeting:       types.SignedLengthString
    house_map_code: types.Int
    rank:           TribeRankInfo

@public
class WhisperPacket(ClientboundTribullePacket):
    id = 66

    sender:    types.SignedLengthString
    community: pak.Enum(types.Int, enums.TribulleCommunity)
    receiver:  types.SignedLengthString
    message:   types.SignedLengthString

@public
class TribeInviteResultPacket(FingerprintedClientboundTribullePacket):
    id = 79

    result: types.Byte

@public
class AnswerTribeInviteResultPacket(FingerprintedClientboundTribullePacket):
    id = 81

    result: types.Byte

@public
class CreateTribeResultPacket(FingerprintedClientboundTribullePacket):
    id = 85

    result: types.Byte

@public
class TribeInvitePacket(ClientboundTribullePacket):
    id = 86

    inviter:    types.SignedLengthString
    tribe_name: types.SignedLengthString

@public
class AnswerTribeInvitePacket(ClientboundTribullePacket):
    id = 87

    target:   types.SignedLengthString
    accepted: types.ByteBoolean

@public
class TribeMemberConnectedPacket(ClientboundTribullePacket):
    id = 88

    username: types.SignedLengthString

@public
class TribeInformationPacket(ClientboundTribullePacket):
    id = 89

    tribe_name:     types.SignedLengthString
    tribe_id:       types.Int
    greeting:       types.SignedLengthString
    house_map_code: types.Int
    rank:           TribeRankInfo

@public
class TribeMemberDisconnectedPacket(ClientboundTribullePacket):
    id = 90

    username: types.SignedLengthString

@public
class TribeMemberJoinedPacket(ClientboundTribullePacket):
    id = 91

    username: types.SignedLengthString

@public
class TribeMemberLeftPacket(ClientboundTribullePacket):
    id = 92

    username: types.SignedLengthString

@public
class ChangeTribeHouseMapResultPacket(FingerprintedClientboundTribullePacket):
    id = 103

    result: types.Byte

@public
class OpenTribeMenuResultPacket(FingerprintedClientboundTribullePacket):
    id = 109

    result: types.Byte

@public
class CloseTribeMenuResultPacket(FingerprintedClientboundTribullePacket):
    id = 111

    result: types.Byte

@public
class ChangeTribeMemberRankResultPacket(FingerprintedClientboundTribullePacket):
    id = 113

    result: types.Byte

@public
class TribeMemberRankChangedPacket(ClientboundTribullePacket):
    id = 124

    initiator: types.SignedLengthString
    target:    types.SignedLengthString
    rank_name: types.SignedLengthString

@public
class TribeMenuPacket(ClientboundTribullePacket):
    id = 130

    tribe_id:       types.Int
    tribe_name:     types.SignedLengthString
    greeting:       types.SignedLengthString
    house_map_code: types.Int

    members: TribeMemberInfo[types.Short]
    ranks:   TribeRankInfo[types.Short]

@public
class TribeMemberInfoPacket(ClientboundTribullePacket):
    id = 131

    member: TribeMemberInfo
