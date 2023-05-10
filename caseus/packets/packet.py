r"""The foundation for Transformice :class:`~.Packet`\s."""

import abc
import pak

from public import public

from ..secrets import Secrets

from .. import types
from .. import util

@public
class PacketCode(pak.Type):
    # TODO: Docs.

    @classmethod
    def _unpack(cls, buf, *, ctx):
        C  = types.UnsignedByte.unpack(buf, ctx=ctx)
        CC = types.UnsignedByte.unpack(buf, ctx=ctx)

        return (C, CC)

    @classmethod
    def _pack(self, value, *, ctx):
        # NOTE: The game when packing the code, allows passing a single
        # integer value and packing it as a short. Although the game does
        # utilize this occasionally, I do not find it compelling to
        # replicate it, and so require every ID to have two components.

        C, CC = value

        return types.UnsignedByte.pack(C, ctx=ctx) + types.UnsignedByte.pack(CC, ctx=ctx)

class _GeneralPacketContext(pak.Packet.Context):
    def __init__(self, secrets=Secrets()):
        self.secrets = secrets

        super().__init__()

    def __hash__(self):
        return hash(self.secrets)

    def __eq__(self, other):
        if not isinstance(other, Packet.Context):
            return NotImplemented

        return self.secrets == other.secrets

@public
class Packet(pak.Packet):
    r"""A Transformice packet.

    The ID should be a pair of :class:`int`\s, such as ``(3, 4)``::

        import caseus

        class MyPacket(caseus.Packet):
            id = (3, 4)

    Other Transformice projects will label these numbers as
    ``(C, CC)`` or sometimes ``CCC`` altogether.
    """

    Context = _GeneralPacketContext

    class Header(pak.Packet.Header):
        id: PacketCode

@public
class ServerboundPacket(Packet):
    r"""A serverbound :class:`Packet`.

    :class:`Packet`\s which are sent to the server should inherit
    from :class:`ServerboundPacket` to be registered as such.
    """

    CIPHER = None

    class Header(pak.Packet.Header):
        fingerprint: types.Byte
        id:          PacketCode

    def __init__(self, *, fingerprint=None, ctx=None, **fields):
        super().__init__(ctx=ctx, **fields)

        self.fingerprint = fingerprint

    @classmethod
    def unpack_with_fingerprint(cls, fingerprint, buf, *, ctx=None):
        packet = cls.unpack(buf, ctx=ctx)

        packet.fingerprint = fingerprint

        return packet

    def __repr__(self):
        return (
            f"{type(self).__qualname__}("

            +

            ", ".join([
                f"fingerprint={repr(self.fingerprint)}",

                *(f"{name}={repr(value)}" for name, value in self.enumerate_field_values())
            ])

            +

            ")"
        )

    @classmethod
    def cipher_data(cls, data, *, fingerprint, ctx):
        if cls.CIPHER is None:
            return data

        return ctx.secrets.cipher(cls.CIPHER, data, fingerprint=fingerprint)

    @classmethod
    def decipher_data(cls, buf, *, fingerprint, ctx):
        if cls.CIPHER is None:
            return buf.read()

        return ctx.secrets.decipher(cls.CIPHER, buf, fingerprint=fingerprint)

@public
class ClientboundPacket(Packet):
    r"""A clientbound :class:`Packet`.

    :class:`Packet`\s which are sent to the client should inherit
    from :class:`ClientboundPacket` to be registered as such.
    """

@public
class TribullePacket(pak.Packet):
    """A packet for the community platform.

    Such packets are used for inter-room and inter-game communication.

    See https://atelier801.fandom.com/wiki/Community_platform
    for more information.

    The name "Tribulle" is jargon from the game's code,
    derived from the French words "tri", meaning "sorting",
    and "bulle", meaning "bubble", which is the jargon the
    game uses to name rooms.
    """

    Context = _GeneralPacketContext

    class Header(pak.Packet.Header):
        id: types.Short

@public
class ServerboundTribullePacket(TribullePacket):
    r"""A serverbound :class:`TribullePacket`.

    :class:`TribullePacket`\s which are sent to the server
    should inherit from :class:`ServerboundTribullePacket`
    to be registered as such.
    """

@public
class ClientboundTribullePacket(TribullePacket):
    r"""A clientbound :class:`TribullePacket`.

    :class:`TribullePacket`\s which are sent to the client
    should inherit from :class:`ClientboundTribullePacket`
    to be registered as such.
    """

@public
class LegacyPacket(pak.Packet, abc.ABC):
    """A legacy packet.

    These packets are from an older time and are of
    a different format from sane packets, the body
    of them being a list of strings.
    """

    # These packets are.. strangely packed.
    # They are backed by string data, and
    # each component of a packet is split by
    # the '\x01' character. The first component
    # contains the ID, and the others are the
    # packet body. Because of this very strange
    # format, we will provide alternatives to
    # certain parts of the normal 'pak.Packet'
    # machinery.

    Context = _GeneralPacketContext

    @classmethod
    @pak.util.cache
    def GenericWithID(cls, id):
        return type(f"{cls.__qualname__}.GenericWithID({repr(id)})", (_GenericLegacyPacket, cls), dict(
            id = id,

            __module__ = cls.__module__,
        ))

    @classmethod
    @abc.abstractmethod
    def _from_body_components(cls, components, *, ctx):
        raise NotImplementedError

    @classmethod
    def from_body_components(cls, components, *, ctx=None):
        if ctx is None:
            ctx = cls.Context()

        return cls._from_body_components(components, ctx=ctx)

    @abc.abstractmethod
    def _body_components(self, *, ctx):
        raise NotImplementedError

    def body_components(self, *, ctx=None):
        if ctx is None:
            ctx = self.Context()

        return self._body_components(ctx=ctx)

    @staticmethod
    def repr_for_attrs(*attrs):
        def genned_repr(self):
            return (
                f"{type(self).__qualname__}("

                +

                ", ".join(
                    f"{attr}={repr(getattr(self, attr))}"

                    for attr in attrs
                )

                +

                ")"
            )

        return genned_repr

class _GenericLegacyPacket(LegacyPacket):
        def __init__(self, body):
            self.body = body

        @classmethod
        def _from_body_components(cls, components, *, ctx):
            return cls(components)

        def _body_components(self, *, ctx):
            return self.body

        __repr__ = LegacyPacket.repr_for_attrs("body")

@public
class ServerboundLegacyPacket(LegacyPacket):
    r"""A serverbound :class:`LegacyPacket`.

    :class:`LegacyPacket`\s which are sent to the server
    should inherit from :class:`ServerboundLegacyPacket`
    to be registered as such.
    """

@public
class ClientboundLegacyPacket(LegacyPacket):
    r"""A clientbound :class:`LegacyPacket`.

    :class:`LegacyPacket`\s which are sent to the client
    should inherit from :class:`ClientboundLegacyPacket`
    to be registered as such.
    """

@public
class ExtensionPacket(pak.Packet):
    """A packet not contained in the vanilla protocol."""

    Context = _GeneralPacketContext

    class Header(pak.Packet.Header):
        id: types.String

@public
class ServerboundExtensionPacket(ExtensionPacket):
    pass

@public
class ClientboundExtensionPacket(ExtensionPacket):
    pass
