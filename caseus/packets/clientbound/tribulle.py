import pak

from public import public

from ..packet import ClientboundTribullePacket
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

    gender:    pak.Enum(types.Byte, enums.Gender)
    global_id: types.Int

    soulmate:  FriendInfo
    friends:   FriendInfo[types.Short]
    blacklist: types.SignedLengthString[types.Short]

    tribe:             TribeInfo
    tribe_rank:        types.SignedLengthString
    tribe_permissions: types.Int

@public
class WhisperPacket(ClientboundTribullePacket):
    id = 66

    sender:    types.SignedLengthString
    community: pak.Enum(types.Int, enums.TribulleCommunity)
    receiver:  types.SignedLengthString
    message:   types.SignedLengthString
