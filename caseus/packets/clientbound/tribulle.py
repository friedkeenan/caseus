import pak

from public import public

from ..packet import ClientboundTribullePacket
from ... import types
from ... import enums

@public
class ConnectedToCommunityPlatformPacket(ClientboundTribullePacket):
    id = 3

    gender:    pak.Enum(types.Byte, enums.Gender)
    global_id: types.Int

    soulmate:  types.FriendDescription
    friends:   types.FriendDescription[types.Short]
    blacklist: types.SignedLengthString[types.Short]

    tribe:             types.TribeDescription
    tribe_rank:        types.SignedLengthString
    tribe_permissions: types.Int

@public
class WhisperPacket(ClientboundTribullePacket):
    id = 66

    sender:    types.SignedLengthString
    community: pak.Enum(types.Int, enums.TribulleCommunity)
    receiver:  types.SignedLengthString
    message:   types.SignedLengthString
