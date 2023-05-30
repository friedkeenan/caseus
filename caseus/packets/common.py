import pak

from public import public

from .. import enums
from .. import types

@public
class _NestedLegacyType(pak.Type):
    parent_cls = None

    @classmethod
    def _unpack(cls, buf, *, ctx):
        data       = types.String.unpack(buf, ctx=ctx)
        components = data.split("\x01")

        id = (ord(components[0][0]), ord(components[0][1]))

        packet_cls = cls.parent_cls.subclass_with_id(id, ctx=ctx.packet_ctx)
        if packet_cls is None:
            packet_cls = cls.parent_cls.GenericWithID(id)

        return packet_cls.from_body_components(components[1:], ctx=ctx.packet_ctx)

    @classmethod
    def _pack(cls, value, *, ctx):
        id              = value.id(ctx=ctx.packet_ctx)
        body_components = value.body_components(ctx=ctx.packet_ctx)

        components = [
            chr(id[0]) + chr(id[1]),

            *body_components
        ]

        return types.String.pack("\x01".join(components), ctx=ctx)

    @classmethod
    def _call(cls, parent_cls):
        return cls.make_type(
            f"{cls.__qualname__}({parent_cls.__qualname__})",

            parent_cls = parent_cls,
        )

# Only used for the 'typelike' machinery.
class _CompressedSubPacketMeta(type):
    pass

@public
class CompressedSubPacket(pak.Packet, metaclass=_CompressedSubPacketMeta):
    @classmethod
    def __class_getitem__(cls, index):
        return _CompressedSubPacketType(cls)[index]

class _CompressedSubPacketType(pak.Type):
    subpacket_cls = None

    @classmethod
    def _default(cls, *, ctx):
        return cls.subpacket_cls(ctx=ctx.packet_ctx)

    @classmethod
    def _unpack(cls, buf, *, ctx):
        packet_buf = types.CompressedByteArray.unpack(buf, ctx=ctx)

        return cls.subpacket_cls.unpack(packet_buf, ctx=ctx.packet_ctx)

    @classmethod
    def _pack(cls, value, *, ctx):
        return types.CompressedByteArray.pack(value.pack(ctx=ctx.packet_ctx), ctx=ctx)

    @classmethod
    def _call(cls, subpacket_cls):
        return cls.make_type(
            f"{cls.__qualname__}({subpacket_cls.__qualname__})",

            subpacket_cls = subpacket_cls
        )

pak.Type.register_typelike(_CompressedSubPacketMeta, _CompressedSubPacketType)

@public
class PlayerInfo(pak.SubPacket):
    username:       types.String
    session_id:     types.Int
    is_shaman:      types.Boolean
    activity:       pak.Enum(types.Byte, enums.PlayerActivity)
    score:          types.Short
    cheeses:        types.Byte
    title_id:       types.Short
    title_stars:    types.Byte
    gender:         pak.Enum(types.Byte, enums.Gender)
    unk_string_10:  types.String # A lot of times it's the string '0' but others it's a string of a different number. Same name as avatar ID seemingly?
    look:           types.String # TODO: Parse outfit.
    unk_boolean_12: types.Boolean
    mouse_color:    types.Int
    shaman_color:   types.Int
    unk_int_15:     types.Int # Staff name color?
    name_color:     types.Int
    context_id:     types.UnsignedByte

@public
class RoomProperties(pak.SubPacket):
    without_shaman_skills:        types.Boolean
    without_physical_consumables: types.Boolean
    without_adventure_maps:       types.Boolean
    with_mice_collisions:         types.Boolean
    with_fall_damage:             types.Boolean
    round_duration_percentage:    types.UnsignedByte
    mice_weight_percentage:       types.Int
    max_players:                  types.Short
    map_rotation:                 pak.Enum(types.Byte, enums.MapCategory)[types.UnsignedByte]

class _ObjectInfo(pak.SubPacket):
    class Attributes(pak.SubPacket):
        x:                pak.ScaledInteger(types.Int,   100 / 30)
        y:                pak.ScaledInteger(types.Int,   100 / 30)
        velocity_x:       pak.ScaledInteger(types.Short, 10)
        velocity_y:       pak.ScaledInteger(types.Short, 10)
        rotation:         pak.ScaledInteger(types.Short, 100)
        angular_velocity: pak.ScaledInteger(types.Short, 100)
        mice_collidable:  types.Boolean
        inactive:         types.Boolean

    object_id:        types.Int
    shaman_object_id: types.Short

    attributes: pak.Optional(Attributes, lambda packet: not packet.should_remove)

    @property
    def should_remove(self):
        return self.shaman_object_id == -1

@public
class ServerboundObjectInfo(_ObjectInfo):
    def clientbound(self, *, add_if_missing=False):
        return ClientboundObjectInfo(
            object_id        = self.object_id,
            shaman_object_id = self.shaman_object_id,
            attributes       = self.attributes,
            add_if_missing   = add_if_missing,
        )

@public
class ClientboundObjectInfo(_ObjectInfo):
    add_if_missing: pak.Optional(types.ByteBoolean, lambda packet: not packet.should_remove)
