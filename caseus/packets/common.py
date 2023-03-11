import pak

from public import public

from .packet import (
    GenericLegacyPacketWithID,
    GenericTribullePacketWithID,
    GenericExtensionPacketWithID,
)

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
            packet_cls = GenericLegacyPacketWithID(id, cls.parent_cls)

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

@public
class _NestedTribulleType(pak.Type):
    parent_cls = None

    @classmethod
    def _unpack(cls, buf, *, ctx):
        header = cls.parent_cls.Header.unpack(buf, ctx=ctx.packet_ctx)

        packet_cls = cls.parent_cls.subclass_with_id(header.id, ctx=ctx.packet_ctx)
        if packet_cls is None:
            packet_cls = GenericTribullePacketWithID(header.id, cls.parent_cls)

        return packet_cls.unpack(buf, ctx=ctx.packet_ctx)

    @classmethod
    def _pack(cls, value, *, ctx):
        return value.pack(ctx=ctx.packet_ctx)

    @classmethod
    def _call(cls, parent_cls):
        return cls.make_type(
            f"{cls.__qualname__}({parent_cls.__qualname__})",

            parent_cls = parent_cls,
        )

@public
class _NestedExtensionType(pak.Type):
    @classmethod
    def _unpack(cls, buf, *, ctx):
        header = cls.parent_cls.Header.unpack(buf, ctx=ctx.packet_ctx)

        packet_cls = cls.parent_cls.subclass_with_id(header.id, ctx=ctx.packet_ctx)
        if packet_cls is None:
            packet_cls = GenericExtensionPacketWithID(header.id, cls.parent_cls)

        return packet_cls.unpack(buf, ctx=ctx.packet_ctx)

    @classmethod
    def _pack(cls, value, *, ctx):
        return value.pack(ctx=ctx.packet_ctx)

    @classmethod
    def _call(cls, parent_cls):
        return cls.make_type(
            f"{cls.__qualname__}({parent_cls.__qualname__})",

            parent_cls = parent_cls,
        )

@public
class _SimpleNestedPacketType(pak.Type):
    parent_cls = None

    @classmethod
    def _default(cls, *, ctx):
        return None

    @classmethod
    def _unpack(cls, buf, *, ctx):
        # NOTE: We forgo contexts here.

        header = cls.parent_cls.Header.unpack(buf)

        packet_cls = cls.parent_cls.subclass_with_id(header.id)
        if packet_cls is None:
            return None

        return packet_cls.unpack(buf)

    @classmethod
    def _pack(cls, value, *, ctx):
        if value is None:
            return b""

        return value.pack()

    @classmethod
    def _call(cls, parent_cls):
        return cls.make_type(
            f"{cls.__qualname__}({parent_cls.__qualname__})",

            parent_cls = parent_cls,
        )
