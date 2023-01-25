import abc
import fixedint
import pak

from public import public

from . import types
from . import util

@public
class Cipher(abc.ABC):
    def __init__(self, name):
        self.name = name

    def cipher_data(self, data, key, *, fingerprint):
        return self._cipher_data(data, key, fingerprint=fingerprint)

    def decipher_data(self, buf, key, *, fingerprint):
        buf = pak.util.file_object(buf)

        return self._decipher_data(buf, key, fingerprint=fingerprint)

    @abc.abstractmethod
    def _cipher_data(self, data, key, *, fingerprint):
        raise NotImplementedError

    @abc.abstractmethod
    def _decipher_data(self, buf, key, *, fingerprint):
        raise NotImplementedError

@public
class XXTEACipher(Cipher):
    def _cipher_data(self, data, key, *, fingerprint):
        # Pad to 8 bytes.
        if len(data) < 8:
            data += bytes(8 - len(data))

        # The size of the data must perfectly fit 'UnsignedInt's.
        offset_from_valid_size = len(data) % types.UnsignedInt.size()
        if offset_from_valid_size != 0:
            data += bytes(types.UnsignedInt.size() - offset_from_valid_size)

        num_blocks = len(data) // types.UnsignedInt.size()

        blocks = types.UnsignedInt[num_blocks].unpack(data)

        util.xxtea_encode_in_place(blocks, key)

        return (
            types.Short.pack(num_blocks) +

            b"".join(types.UnsignedInt.pack(block) for block in blocks)
        )

    def _decipher_data(self, buf, key, *, fingerprint):
        num_blocks = types.Short.unpack(buf)

        blocks = types.UnsignedInt[num_blocks].unpack(buf)

        util.xxtea_decode_in_place(blocks, key)

        return b"".join(
            types.UnsignedInt.pack(block) for block in blocks
        )

@public
class XORCipher(Cipher):
    def name(self):
        return self._name

    def _cipher_data(self, data, key, *, fingerprint):
        key_len = len(key)

        return bytes((byte ^ key[i % key_len]) & 0xFF for i, byte in enumerate(data, start=fingerprint + 1))

    def _decipher_data(self, buf, key, *, fingerprint):
        key_len = len(key)

        return bytes((byte ^ key[i % key_len]) & 0xFF for i, byte in enumerate(buf.read(), start=fingerprint + 1))

public(IDENTIFICATION = XXTEACipher("identification"))

public(XOR = XORCipher("msg"))

@public
class Secrets:
    def __init__(self, key_sources):
        self.key_sources = tuple(key_sources)

    def __hash__(self):
        return hash(self.key_sources)

    def __eq__(self, other):
        if not isinstance(other, Secrets):
            return NotImplementedError

        return self.key_sources == other.key_sources

    @staticmethod
    @pak.util.cache
    def _key(key_sources, name):
        # TODO: Better name.
        num = fixedint.Int32(0x1505)

        for i, source_num in enumerate(key_sources):
            num = (num << 5) + num + source_num + ord(name[i % len(name)])

        key = []
        for _ in range(len(key_sources)):
            num ^= num << 13
            num ^= num >> 17
            num ^= num << 5

            key.append(int(num))

        return key

    def key(self, name):
        return self._key(self.key_sources, name)

    # NOTE: We don't use any contexts here.
    # TODO: Think about whether we should.

    def cipher(self, cipher, data, *, fingerprint=None):
        return cipher.cipher_data(data, self.key(cipher.name), fingerprint=fingerprint)

    def decipher(self, cipher, buf, *, fingerprint=None):
        return cipher.decipher_data(buf, self.key(cipher.name), fingerprint=fingerprint)
