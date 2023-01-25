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
