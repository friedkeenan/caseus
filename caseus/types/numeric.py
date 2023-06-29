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
class VarNumBufferLengthError(Exception):
    """An error indicating the number of bytes read would exceed
    the allowed storage of a :class:`VarNum`.

    Parameters
    ----------
    var_num_cls : subclass of :class:`VarNum`
        The subclass whose storage would be exceeded.
    """

    def __init__(self, var_num_cls):
        super().__init__(f"'{var_num_cls.__qualname__}' cannot read beyond {var_num_cls._max_bytes} bytes")

@public
class VarNumOutOfRangeError(Exception):
    """An error indicating a value is outside the range of a :class:`VarNum`'s possible values.

    Parameters
    ----------
    var_num_cls : subclass of :class:`VarNum`
        The subclass whose range ``value`` lies outside of.
    value : :class:`int`
        The value which exceeds the range.
    """

    def __init__(self, var_num_cls, value):
        super().__init__(f"Value '{value}' is out of the range of '{var_num_cls.__qualname__}'")

@public
class VarNum(pak.Type):
    r"""A signed, variable-length integer.

    :meta no-undoc-members:

    Each byte of raw data contains 7 bits that contribute to the
    value of the integer, and 1 bit that indicates whether to
    read the next byte.

    If you are familiar with Minecraft's VarInts or VarLongs, these
    are equivalent to those. Transformice uses a :class:`VarInt` for
    the length of sent and received :class:`~.Packet`\s.

    When unpacking, if the number of bytes read would exceed the
    maximum number of bytes needed to read the specified :attr:`bits`,
    then a :exc:`VarNumBufferLengthError` is raised. This stops data
    from being read forever, potentially causing a denial of service.

    When packing, if the value to pack is outside the range of possible
    values for the specified :attr:`bits`, then a :exc:`VarNumOutOfRangeError`
    is raised. This stops values from being sent which may not be
    accurately received.

    Attributes
    ----------
    bits : :class:`int`
        The maximum number of bits the integer can contain.
    """

    _default = 0

    bits = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Calculate the maximum number of bytes to read
        if cls.bits is not None:
            # Each byte has 7 value-bits, and 1 bit for whether to read the next byte.
            cls._max_bytes = math.ceil(cls.bits / 7)

            cls._value_range = range(-pak.util.bit(cls.bits - 1), pak.util.bit(cls.bits - 1))

    @classmethod
    def _unpack(cls, buf, *, ctx):
        num = 0

        for i in range(cls._max_bytes):
            read = UnsignedByte.unpack(buf, ctx=ctx)

            # Get the bottom 7 bits
            value = read & 0b01111111

            num |= value << (7 * i)

            # If the top bit is not set, return
            if read & 0b10000000 == 0:
                return pak.util.to_signed(num, bits=cls.bits)

        raise VarNumBufferLengthError(cls)

    @classmethod
    def _pack(cls, value, *, ctx):
        # If 'value' is not an 'int' then checking if it's contained will
        # loop through the (very large) value range instead of just checking
        # comparisons.
        if not isinstance(value, int) or value not in cls._value_range:
            raise VarNumOutOfRangeError(cls, value)

        value = pak.util.to_unsigned(value, bits=cls.bits)

        data = b""

        while True:
            # Get the bottom 7 bits.
            to_write = value & 0b01111111

            value >>= 7
            if value != 0:
                # Set the top bit.
                to_write |= 0b10000000

            data += UnsignedByte.pack(to_write, ctx=ctx)

            if value == 0:
                return data

@public
class VarInt(VarNum):
    r"""A signed, variable-length 32-bit integer.

    Equivalent to a VarInt in Minecraft's packet protocol.
    Transformice uses them for the length of sent and received
    :class:`~.Packet`\s. The length of :class:`~.Packet`\s in
    Transformice's code could be unpacked into a negative
    integer, and when packing the length, negative values are
    packed correctly, truly making the format the same as
    Minecraft's VarInt.
    """

    bits = 32

# TODO: Actually implement the limit.
public(LimitedLEB128 = pak.LEB128)
