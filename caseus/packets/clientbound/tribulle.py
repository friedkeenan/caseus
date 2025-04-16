import pak

from public import public

from ..packet import ClientboundTribullePacket, FingerprintedClientboundTribullePacket
from ... import types
from ... import enums

@public
class ConnectedToCommunityPlatformPacket(ClientboundTribullePacket):
    id = 3

    class FriendInfo(pak.SubPacket):
        global_id:     types.Int
        name:          types.SignedLengthString
        gender:        pak.Enum(types.Byte, enums.Gender)
        avatar_id:     types.Int
        bidirectional: types.ByteBoolean
        connected:     types.ByteBoolean
        game_id:       types.Int
        room_name:     types.SignedLengthString
        last_login:    types.Int

    class TribeInfo(pak.SubPacket):
        name:           types.SignedLengthString
        tribe_id:       types.Int
        greeting:       types.SignedLengthString
        house_map_code: types.Int

    class RankInfo(pak.SubPacket):
        name:        types.SignedLengthString
        permissions: types.Int

    gender:    pak.Enum(types.Byte, enums.Gender)
    global_id: types.Int

    soulmate:  FriendInfo
    friends:   FriendInfo[types.Short]
    blacklist: types.SignedLengthString[types.Short]

    tribe_name:     types.SignedLengthString
    tribe_id:       types.Int
    greeting:       types.SignedLengthString
    house_map_code: types.Int
    tribe_rank:     RankInfo

@public
class WhisperPacket(ClientboundTribullePacket):
    id = 66

    sender:    types.SignedLengthString
    community: pak.Enum(types.Int, enums.TribulleCommunity)
    receiver:  types.SignedLengthString
    message:   types.SignedLengthString

@public
class ChangeTribeHouseMapResultPacket(FingerprintedClientboundTribullePacket):
    id = 103

    # TODO: Enum?
    result: types.Byte

@public
class GetTribeSettingsResultPacket(FingerprintedClientboundTribullePacket):
    id = 109

    # TODO: Enum?
    result: types.Byte

@public
class TribeSettingsPacket(ClientboundTribullePacket):
    id = 130

    class MemberInfo(pak.SubPacket):
        class LocationInfo(pak.SubPacket):
            service_id: types.Int
            room_name:  types.SignedLengthString

        global_id: types.Int
        username:  types.SignedLengthString

        gender:     pak.Enum(types.Byte, enums.Gender)
        avatar_id:  types.Int
        last_login: types.Int
        rank_index: types.Byte

        location: LocationInfo

    class RankInfo(pak.SubPacket):
        name:        types.SignedLengthString
        permissions: types.Int

    tribe_id:       types.Int
    tribe_name:     types.SignedLengthString
    greeting:       types.SignedLengthString
    house_map_code: types.Int

    members: MemberInfo[types.Short]
    ranks:   RankInfo[types.Short]
