import dataclasses
import typing
import pak

from public import *

from .. import enums

from .numeric import (
    Boolean,
    Byte,
    ByteBoolean,
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
        session_id     = Int,
        is_shaman      = Boolean,
        activity       = pak.Enum(Byte, enums.PlayerActivity),
        score          = Short,
        cheeses        = Byte,
        title_id       = Short,
        title_stars    = Byte,
        gender         = _Gender,
        unk_string_10  = String, # A lot of times it's the string '0' but others it's a string of a different number. Same name as avatar ID seemingly?
        outfit_code    = String, # TODO: Parse outfit.
        unk_boolean_12 = Boolean,
        mouse_color    = Int,
        shaman_color   = Int,
        unk_int_15     = Int, # Staff name color?
        name_color     = Int,
        context_id     = UnsignedByte,
    )
)

public(
    RoomPropertiesDescription = pak.Compound(
        "RoomPropertiesDescription",

        without_shaman_skills        = Boolean,
        without_physical_consumables = Boolean,
        without_adventure_maps       = Boolean,
        with_mice_collisions         = Boolean,
        without_fall_damage          = Boolean,
        round_duration_percentage    = UnsignedByte,
        mice_weight_percentage       = Int,
        max_players                  = Short,
        map_rotation                 = pak.Enum(Byte, enums.MapCategory)[UnsignedByte],
    )
)

@public
class ObjectDescription(pak.Type):
    @dataclasses.dataclass
    class _Description:
        object_id:        int
        shaman_object_id: int
        x:                float = 0.0
        y:                float = 0.0
        velocity_x:       float = 0.0
        velocity_y:       float = 0.0
        rotation:         float = 0.0
        angular_velocity: float = 0.0
        mice_collidable:  bool  = False
        inactive:         bool  = False

        @property
        def should_remove(self):
            return self.shaman_object_id == -1

    class ServerboundDescription(_Description):
        def clientbound(self, *, add_if_missing=False):
            return ObjectDescription.ClientboundDescription(
                object_id        = self.object_id,
                shaman_object_id = self.shaman_object_id,
                x                = self.x,
                y                = self.y,
                velocity_x       = self.velocity_x,
                velocity_y       = self.velocity_y,
                rotation         = self.rotation,
                angular_velocity = self.angular_velocity,
                mice_collidable  = self.mice_collidable,
                inactive         = self.inactive,

                add_if_missing = add_if_missing,
            )

    @dataclasses.dataclass
    class ClientboundDescription(_Description):
        add_if_missing: bool = False

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls._serverbound = issubclass(cls.Description, cls.ServerboundDescription)

    @classmethod
    def _unpack(cls, buf, *, ctx):
        object_id = Int.unpack(buf, ctx=ctx)
        shaman_object_id = Short.unpack(buf, ctx=ctx)

        if shaman_object_id == -1:
            return cls.Description(object_id, -1)

        if cls._serverbound:
            return cls.Description(
                object_id        = object_id,
                shaman_object_id = shaman_object_id,

                x                = Int.unpack(buf, ctx=ctx) * 30 / 100,
                y                = Int.unpack(buf, ctx=ctx) * 30 / 100,
                velocity_x       = Short.unpack(buf, ctx=ctx) / 10,
                velocity_y       = Short.unpack(buf, ctx=ctx) / 10,
                rotation         = Short.unpack(buf, ctx=ctx) / 100,
                angular_velocity = Short.unpack(buf, ctx=ctx) / 100,
                mice_collidable  = Boolean.unpack(buf, ctx=ctx),
                inactive         = Boolean.unpack(buf, ctx=ctx),
            )

        return cls.Description(
            object_id        = object_id,
            shaman_object_id = shaman_object_id,

            x                = Int.unpack(buf, ctx=ctx) * 30 / 100,
            y                = Int.unpack(buf, ctx=ctx) * 30 / 100,
            velocity_x       = Short.unpack(buf, ctx=ctx) / 10,
            velocity_y       = Short.unpack(buf, ctx=ctx) / 10,
            rotation         = Short.unpack(buf, ctx=ctx) / 100,
            angular_velocity = Short.unpack(buf, ctx=ctx) / 100,
            mice_collidable  = Boolean.unpack(buf, ctx=ctx),
            inactive         = Boolean.unpack(buf, ctx=ctx),

            add_if_missing = ByteBoolean.unpack(buf, ctx=ctx),
        )

    @classmethod
    def _pack(cls, value, *, ctx):
        data = (
            Int.pack(value.object_id, ctx=ctx) +

            Short.pack(value.shaman_object_id, ctx=ctx)
        )

        if value.shaman_object_id == -1:
            return data

        data += (
            Int.pack(int(value.x * 100 / 30), ctx=ctx) +
            Int.pack(int(value.y * 100 / 30), ctx=ctx) +

            Short.pack(int(value.velocity_x * 10), ctx=ctx) +
            Short.pack(int(value.velocity_y * 10), ctx=ctx) +

            Short.pack(int(value.rotation         * 100), ctx=ctx) +
            Short.pack(int(value.angular_velocity * 100), ctx=ctx) +

            Boolean.pack(value.mice_collidable, ctx=ctx) +
            Boolean.pack(value.inactive,        ctx=ctx)
        )

        if cls._serverbound:
            return data

        return data + ByteBoolean.pack(value.add_if_missing, ctx=ctx)

    @classmethod
    def _call(cls, *, serverbound):
        if serverbound:
            return cls.make_type(
                cls.__name__,

                Description = cls.ServerboundDescription,
            )

        return cls.make_type(
            cls.__name__,

            Description = cls.ClientboundDescription,
        )

@public
class OwnedShopItemDescription(pak.Type):
    @dataclasses.dataclass
    class Description:
        unique_id: int
        colors:    typing.Optional[list]

    @classmethod
    def _unpack(cls, buf, *, ctx):
        num_colors = Byte.unpack(buf, ctx=ctx)
        unique_id  = Int.unpack(buf, ctx=ctx)

        if num_colors == 0:
            colors = None
        else:
            # NOTE: Our use of 'range' will handle non-positive lengths.
            colors = [Int.unpack(buf, ctx=ctx) for _ in range(num_colors - 1)]

        return cls.Description(unique_id, colors)

    @classmethod
    def _pack(cls, value, *, ctx):
        if value.colors is None:
            packed_colors_len = Byte.pack(0, ctx=ctx)
            packed_colors     = b""
        else:
            packed_colors_len = Byte.pack(len(value.colors) + 1, ctx=ctx)
            packed_colors     = b"".join(
                Int.pack(color) for color in value.colors
            )

        return (
            packed_colors_len                  +
            Int.pack(value.unique_id, ctx=ctx) +
            packed_colors
        )

@public
class OwnedShamanObjectDescription(pak.Type):
    @dataclasses.dataclass
    class Description:
        shaman_object_id: int
        equipped:         bool
        colors:           typing.Optional[list]

    @classmethod
    def _unpack(cls, buf, *, ctx):
        shaman_object_id = Short.unpack(buf, ctx=ctx)
        equipped = Boolean.unpack(buf, ctx=ctx)
        num_colors = Byte.unpack(buf, ctx=ctx)

        if num_colors == 0:
            colors = None
        else:
            # NOTE: Our use of 'range' will handle non-positive lengths.
            colors = [Int.unpack(buf, ctx=ctx) for _ in range(num_colors - 1)]

        return cls.Description(shaman_object_id, equipped, colors)

    @classmethod
    def _pack(cls, value, *, ctx):
        if value.colors is None:
            packed_colors = Byte.pack(0, ctx=ctx)
        else:
            packed_colors = Byte.pack(len(value.colors) + 1, ctx=ctx) + b"".join(
                Int.pack(color) for color in value.colors
            )

        return (
            Short.pack(value.shaman_object_id, ctx=ctx) +
            Boolean.pack(value.equipped,       ctx=ctx) +

            packed_colors
        )
