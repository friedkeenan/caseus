import dataclasses
import pak

from public import *

from .. import enums

from .numeric import (
    Boolean,
    Byte,
    UnsignedByte,
    Short,
    Int,
)
from .string import String, SignedLengthString

_Gender = pak.Enum(Byte, enums.Gender)

@public
class FriendDescription(pak.Type):
    @dataclasses.dataclass
    class Description:
        id:            int
        name:          str
        gender:        enums.Gender
        avatar_id:     int
        bidirectional: bool
        connected:     bool
        game_id:       int
        room_name:     str
        last_login:    int

    @classmethod
    def _unpack(cls, buf, *, ctx):
        return cls.Description(
            id            = Int.unpack(buf, ctx=ctx),
            name          = SignedLengthString.unpack(buf, ctx=ctx),
            gender        = _Gender.unpack(buf, ctx=ctx),
            avatar_id     = Int.unpack(buf, ctx=ctx),
            bidirectional = Byte.unpack(buf, ctx=ctx) != 0,
            connected     = Byte.unpack(buf, ctx=ctx) != 0,
            game_id       = Int.unpack(buf, ctx=ctx),
            room_name     = SignedLengthString.unpack(buf, ctx=ctx),
            last_login    = Int.unpack(buf, ctx=ctx),
        )

    @classmethod
    def _pack(cls, value, *, ctx):
        return (
            Int.pack(value.id, ctx=ctx)                         +
            SignedLengthString.pack(value.name, ctx=ctx)        +
            _Gender.pack(value.gender, ctx=ctx)                 +
            Int.pack(value.avatar_id, ctx=ctx)                  +
            Byte.pack(1 if value.bidirectional else 0, ctx=ctx) +
            Byte.pack(1 if value.connected else 0, ctx=ctx)     +
            Int.pack(value.game_id, ctx=ctx)                    +
            SignedLengthString.pack(value.room_name, ctx=ctx)   +
            Int.pack(value.last_login, ctx=ctx)
        )

@public
class TribeDescription(pak.Type):
    @dataclasses.dataclass
    class Description:
        name: str
        id: int
        greeting: str
        house_map: int

    @classmethod
    def _unpack(cls, buf, *, ctx):
        return cls.Description(
            name      = SignedLengthString.unpack(buf, ctx=ctx),
            id        = Int.unpack(buf, ctx=ctx),
            greeting  = SignedLengthString.unpack(buf, ctx=ctx),
            house_map = Int.unpack(buf, ctx=ctx),
        )

    @classmethod
    def _pack(cls, value, *, ctx):
        return (
            SignedLengthString.pack(value.name, ctx=ctx)     +
            Int.pack(value.id, ctx=ctx)                      +
            SignedLengthString.pack(value.greeting, ctx=ctx) +
            Int.pack(value.house_map, ctx=ctx)
        )

public(
    PlayerDescription = pak.Compound(
        "PlayerDescription",

        username       = String,
        room_id        = Int,
        is_shaman      = Boolean,
        deaths         = Byte, # TODO: Better figure out what this is.
        score          = Short,
        cheeses        = Byte,
        title_id       = Short,
        title_stars    = Byte,
        gender         = _Gender,
        unk_string_10  = String,
        outfit_code    = String, # TODO: Parse outfit.
        unk_boolean_12 = Boolean,
        mouse_color    = Int,
        shaman_color   = Int,
        unk_int_15     = Int,
        name_color     = Int,
        unk_ubyte_17   = UnsignedByte,
    )
)
