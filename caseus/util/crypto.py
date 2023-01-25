import base64
import hashlib
import pak

from public import public

from .. import types

_SHAKIKOO_SALT = (
    b"\xF7\x1A\xA6\xDE\x8F\x17\x76\xA8\x03\x9D\x32\xB8\xA1\x56\xB2\xA9"
    b"\x3E\xDD\x43\x9D\xC5\xDD\xCE\x56\xD3\xB7\xA4\x05\x4A\x0D\x08\xB0"
)

@public
def shakikoo(data):
    """Hashes a string according to the SHAKikoo algorithm.

    Transformice uses this for hashing passwords.

    Parameters
    ----------
    data : :class:`str` or :class:`bytes`
        The data to hash.

        If :class:`str`, then the string is encoded
        in UTF-8 and the result is sued as the data.
    """

    if isinstance(data, str):
        data = data.encode("utf-8")

    # Hash the data with SHA-256.
    base_hash = hashlib.sha256(data)

    # Get the hex digest of the hash, convert it to bytes, and add the salt.
    new_data = base_hash.hexdigest().encode("utf-8") + _SHAKIKOO_SALT

    # Hash the new data again.
    extra_hash = hashlib.sha256(new_data)

    # Convert the binary digest to base64.
    return base64.b64encode(extra_hash.digest())

_XXTEA_DELTA = 0x9e3779b9
_MAX_UINT32  = 0xFFFFFFFF

def _MX(e, p, y, z, sum, key):
    return (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum ^ y) + (key[(p & 3) ^ e] ^ z))

@public
def xxtea_encode_in_place(blocks, key):
    """Encodes data according to the XXTEA algorithm.

    Parameters
    ----------
    blocks : :class:`list` of :class:`int`
        The blocks of data to encode.
    key : :class:`list` of :class:`int`
        The key to encode the data with.
    """

    # See https://en.wikipedia.org/wiki/XXTEA for a
    # description and reference implementation.
    #
    # This implementation is however based on
    # the one contained in Transformice, which
    # is shaped a little differently.

    n   = len(blocks)
    z   = blocks[n - 1]
    sum = 0

    for _ in range(6 + 52 // n):
        sum += _XXTEA_DELTA

        # Deal with potential overflow.
        sum &= _MAX_UINT32

        e = (sum >> 2) & 3

        for p in range(n):
            y = blocks[(p + 1) % n]

            blocks[p] += _MX(e, p, y, z, sum, key)

            # Deal with potential overflow.
            blocks[p] &= _MAX_UINT32

            z = blocks[p]

@public
def xxtea_decode_in_place(blocks, key):
    """Decodes data according to the XXTEA algorithm.

    Parameters
    ----------
    blocks : :class:`list` of :class:`int`
        The blocks of data to decode.
    key : :class:`list` of :class:`int`
        The key to decode the data with.
    """

    # See https://en.wikipedia.org/wiki/XXTEA for a
    # description and reference implementation.

    n = len(blocks)
    y = blocks[0]

    cycles = 6 + 52 // n
    sum = cycles * _XXTEA_DELTA

    # Deal with potential overflow.
    sum &= _MAX_UINT32

    while sum > 0:
        e = (sum >> 2) & 3

        for p in range(n - 1, -1, -1):
            # NOTE: When 'p' is 0, this will get the last element.
            z = blocks[p - 1]

            blocks[p] -= _MX(e, p, y, z, sum, key)

            # Deal with potential underflow.
            blocks[p] &= _MAX_UINT32

            y = blocks[p]

        sum -= _XXTEA_DELTA

        # Deal with potential underflow.
        sum &= _MAX_UINT32
