"""Types relating to strings."""

import pak
import zlib

from public import public

from .numeric import (
    UnsignedShort,
    Short,
    Int,
)

public(String = pak.PrefixedString(UnsignedShort))

public(SignedLengthString = pak.PrefixedString(Short))

class _UInt24(pak.Type):
    _size    = 3
    _default = 0

    @classmethod
    def _unpack(cls, buf, *, ctx):
        data = buf.read(3)

        return (
            data[0] << 16 |
            data[1] <<  8 |
            data[2]
        )

    @classmethod
    def _pack(cls, value, *, ctx):
        return bytes([
            (value >> 16) & 0xFF,
            (value >>  8) & 0xFF,
            (value >>  0) & 0xFF,
        ])

public(LargeString = pak.PrefixedString(_UInt24))

@public
class CompressedByteArray(pak.Type):
    _default = bytearray()

    def __set__(self, instance, value):
        return super().__set__(instance, bytearray(value))

    @classmethod
    def _unpack(cls, buf, *, ctx):
        compressed_length = Int.unpack(buf, ctx=ctx)
        if compressed_length == 0:
            return bytearray()

        compressed_data = buf.read(compressed_length)
        if len(compressed_data) < compressed_length:
            raise pak.util.BufferOutOfDataError("Reading compressed data failed")

        return zlib.decompress(compressed_data)

    @classmethod
    def _pack(cls, value, *, ctx):
        compressed_data = zlib.compress(value)

        return Int.pack(len(compressed_data), ctx=ctx) + compressed_data

@public
class CompressedString(pak.Type):
    _default = ""

    @classmethod
    def _unpack(cls, buf, *, ctx):
        return CompressedByteArray.unpack(buf, ctx=ctx).decode("utf-8")

    @classmethod
    def _pack(cls, value, *, ctx):
        return CompressedByteArray.pack(value.encode("utf-8"), ctx=ctx)

@public
class ShiftedString(pak.Type):
    _default = ""

    @classmethod
    def _shift_amount(cls, *, ctx):
        shift_amount = ctx.secrets.game_version % 5

        return shift_amount

    @classmethod
    def _unpack(cls, buf, *, ctx):
        if ctx.is_bot_role() or ctx.secrets.game_version is None:
            # The bot role secrets don't know
            # the actual game version, so don't
            # bother trying to unshift the string.

            return String.unpack(buf, ctx=ctx)

        data_length = UnsignedShort.unpack(buf, ctx=ctx)

        data = buf.read(data_length)
        if len(data) < data_length:
            raise pak.util.BufferOutOfDataError("Reading shifted string data failed")

        shift_amount = cls._shift_amount(ctx=ctx)

        return bytes((byte + shift_amount) & 0xFF for byte in data).decode()

    @classmethod
    def _pack(cls, value, *, ctx):
        if ctx.is_bot_role() or ctx.secrets.game_version is None:
            # The bot role secrets don't know
            # the actual game version, so don't
            # bother trying to unshift the string.

            return String.pack(value, ctx=ctx)

        shift_amount = cls._shift_amount(ctx=ctx)

        data = bytes((byte - shift_amount) & 0xFF for byte in value.encode())

        return UnsignedShort.pack(len(data), ctx=ctx) + data
