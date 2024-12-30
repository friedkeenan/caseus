"""Numeric types.

The names for these types are based on the names from
`ByteArray <https://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/flash/utils/ByteArray.html>`_
methods so that our :class:`~.Packet` definitions may use
the same terminology, despite the imprecise nature of the names.

All numeric types are big endian.
"""

# NOTE: In actionscript, 'writeByte' and 'writeShort'
# are able to write both signed and unsigned values,
# only taking the bottom 8 or 16 bits of their parameters.
# This poses a problem for us, as writing a byte could
# write values from -128 to 255, but reading a byte
# could only result in values from -128 to 127. For
# clientbound packets this is largely okay, since
# 'readByte' and 'readShort' will only ever read signed
# values, however for serverbound packets, the client
# could use 'writeByte' or 'writeShort' to write unsigned
# values without it being readily apparent, and we are
# unable to look at how the server interprets such fields
# to see if they are signed or unsigned. This is quite annoying.

import math
import pak

from public import public

@public
class Boolean(pak.Bool):
    """A single byte truth-value."""

    endian = ">"

@public
class Byte(pak.Int8):
    """A signed 8-bit integer."""

    endian = ">"

# TODO: Actually implement this.
# Also go through each boolean field and see if it's really one of these.
public(ByteBoolean = Boolean)

@public
class UnsignedByte(pak.UInt8):
    """An unsigned 8-bit integer."""

    endian = ">"

@public
class Short(pak.Int16):
    """A signed 16-bit integer."""

    endian = ">"

@public
class UnsignedShort(pak.UInt16):
    """An unsigned 16-bit integer."""

    endian = ">"

@public
class Int(pak.Int32):
    """A signed 32-bit integer."""

    endian = ">"

@public
class UnsignedInt(pak.UInt32):
    """An unsigned 32-bit integer."""

    endian = ">"

@public
class Float(pak.Float32):
    """A 32-bit floating point value."""

    endian = ">"

@public
class Double(pak.Float64):
    """A 64-bit floating point value."""

    endian = ">"

@public
class PacketLength(pak.Type):
    r"""A signed, variable-length 32-bit integer.

    Equivalent to a VarInt in Minecraft's packet protocol.
    Transformice uses them for the length of sent and received
    :class:`~.Packet`\s. The length of :class:`~.Packet`\s in
    Transformice's code could be unpacked into a negative
    integer, and when packing the length, negative values are
    packed correctly, truly making the format the same as
    Minecraft's VarInt.
    """

    _default = 0

    _uleb128 = pak.ULEB128.Limited(max_bytes=5)

    @classmethod
    def _unpack(cls, buf, *, ctx):
        return pak.util.to_signed(cls._uleb128.unpack(buf, ctx=ctx), bits=32)

    @classmethod
    async def _unpack_async(cls, reader, *, ctx):
        return pak.util.to_signed(await cls._uleb128.unpack_async(reader, ctx=ctx), bits=32)

    @classmethod
    def _pack(cls, value, *, ctx):
        return cls._uleb128.pack(pak.util.to_unsigned(value, bits=32), ctx=ctx)

# NOTE: This actually allows 35 bits, and not just 32.
# I'm okay with that, and additionally I think Transformice's
# implementation would be broken for certain values even
# within the 32-bit range, namely very large negative numbers.
public(LEB128 = pak.LEB128.Limited(max_bytes=5))
