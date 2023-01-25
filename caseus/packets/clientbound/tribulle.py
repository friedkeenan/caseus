import pak

from public import public

from ..packet import ClientboundTribullePacket
from ... import types
from ... import enums

@public
class LoginInformation(ClientboundTribullePacket):
    id = 3

    gender: pak.Enum(types.Byte, enums.Gender)

    # Seemingly always '0'.
    player_id: types.Int

    soulmate:  types.FriendDescription
    friends:   types.FriendDescription[types.Short]
    blacklist: types.SignedLengthString[types.Short]

    tribe:             types.TribeDescription
    tribe_rank:        types.SignedLengthString
    tribe_permissions: types.Int
