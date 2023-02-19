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
class CompressedString(pak.Type):
    _default = ""

    @classmethod
    def _unpack(cls, buf, *, ctx):
        compressed_length = Int.unpack(buf, ctx=ctx)
        if compressed_length == 0:
            return ""

        compressed_data = buf.read(compressed_length)
        if len(compressed_data) < compressed_length:
            raise pak.util.BufferOutOfData("Reading compressed data failed")

        data = zlib.decompress(compressed_data)

        return data.decode("utf-8")

    @classmethod
    def _pack(cls, value, *, ctx):
        data = value.encode("utf-8")

        compressed_data = zlib.compress(data)

        return Int.pack(len(compressed_data), ctx=ctx) + compressed_data
