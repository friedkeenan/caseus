import abc
import contextlib
import subprocess
import sys
import fixedint
import pak

from pathlib import Path

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
            types.UnsignedShort.pack(num_blocks) +

            b"".join(types.UnsignedInt.pack(block) for block in blocks)
        )

    def _decipher_data(self, buf, key, *, fingerprint):
        num_blocks = types.UnsignedShort.unpack(buf)

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
    _FIELDS = (
        "server_address",
        "version",
        "connection_token",
        "auth_key",
        "packet_key_sources",
        "client_verification_template",
    )

    correct_loader_size = 0x7EE88

    def __init__(
        self,
        *,
        server_address               = None,
        version                      = None,
        connection_token             = None,
        auth_key                     = None,
        packet_key_sources           = None,
        client_verification_template = None,
    ):
        if packet_key_sources is not None:
            packet_key_sources = tuple(packet_key_sources)

        self.server_address               = server_address
        self.version                      = version
        self.connection_token             = connection_token
        self.auth_key                     = auth_key
        self.packet_key_sources           = packet_key_sources
        self.client_verification_template = client_verification_template

    @staticmethod
    def _debug_config_file_path():
        return Path("~/mm.cfg").expanduser()

    @staticmethod
    def _debug_log_file_path():
        if sys.platform == "linux":
            return Path("~/.macromedia/Flash_Player/Logs/flashlog.txt").expanduser()

        if sys.platform == "win32":
            return Path("~/AppData/Roaming/Macromedia/Flash Player/Logs/flashlog.txt").expanduser()

        # Darwin.
        return Path("~/Library/Preferences/Macromedia/Flash Player/Logs/flashlog.txt").expanduser()

    @staticmethod
    @contextlib.contextmanager
    def _cleanup_debug_configs(config, backup_config):
        try:
            yield

        finally:
            config.unlink()

            if backup_config is not None:
                backup_config.rename(config)

    @staticmethod
    def _parse_field(name, value):
        # TODO: When Python 3.9 support is dropped,
        # use a 'match' statement here.
        if name == "Server Address":
            return "server_address", value

        if name == "Game Version":
            return "version", int(value)

        if name == "Connection Token":
            return "connection_token", value

        if name == "Auth Key":
            return "auth_key", int(value)

        if name == "Packet Key Sources":
            return "packet_key_sources", [int(x) for x in value.split(",")]

        if name == "Client Verification Template":
            return "client_verification_template", bytes.fromhex(value)

        raise ValueError(f"Unknown secret: '{name}' with value {repr(value)}")

    @classmethod
    def load_from_leaker_swf(cls, leaker_swf_path, *, debug_standalone="flashplayerdebugger"):
        if sys.platform not in ("linux", "win32", "darwin"):
            raise ValueError(f"Unsupported platform: '{sys.platform}'")

        leaker_swf_path = Path(leaker_swf_path).resolve()

        config = cls._debug_config_file_path()

        backup_config = None
        if config.exists():
            backup_config = Path("mm.cfg.bak")
            if backup_config.exists():
                raise ValueError(f"Backup config already exists: {backup_config}")

            config.rename(backup_config)

        with config.open("w") as f:
            f.write("TraceOutputFileEnable=1")

        with cls._cleanup_debug_configs(config, backup_config):
            subprocess.run([debug_standalone, leaker_swf_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        log = cls._debug_log_file_path()

        fields = {}
        with log.open() as f:
            for line in f:
                name, value = line.split(":", 1)
                value = value.strip()

                field, parsed_value = cls._parse_field(name, value)

                fields[field] = parsed_value

        return cls(**fields)

    def copy(self, **fields):
        for field in self._FIELDS:
            fields.setdefault(field, getattr(self, field))

        return type(self)(**fields)

    def __setattr__(self, attr, value):
        if hasattr(self, "client_verification_template"):
            raise TypeError(f"'{type(self).__qualname__}' is immutable")

        super().__setattr__(attr, value)

    def _fields(self):
        return tuple((field, getattr(self, field)) for field in self._FIELDS)

    def __hash__(self):
        return hash(self._fields())

    def __eq__(self, other):
        if not isinstance(other, Secrets):
            return NotImplemented

        return self._fields() == other._fields()

    def __repr__(self):
        return (
            f"{type(self).__qualname__}(" +

            ", ".join(
                f"{field}={repr(value)}"

                for field, value in self._fields()
            ) +

            ")"
        )

    @staticmethod
    @pak.util.cache
    def _key(packet_key_sources, name):
        # TODO: Better name.
        num = fixedint.Int32(0x1505)

        for i, source_num in enumerate(packet_key_sources):
            num = (num << 5) + num + source_num + ord(name[i % len(name)])

        key = []
        for _ in range(len(packet_key_sources)):
            num ^= num << 13
            num ^= num >> 17
            num ^= num << 5

            key.append(int(num))

        return key

    def key(self, name):
        return self._key(self.packet_key_sources, name)

    # NOTE: We don't use any contexts here.
    # TODO: Think about whether we should.

    def cipher(self, cipher, data, *, fingerprint=None):
        return cipher.cipher_data(data, self.key(cipher.name), fingerprint=fingerprint)

    def decipher(self, cipher, buf, *, fingerprint=None):
        return cipher.decipher_data(buf, self.key(cipher.name), fingerprint=fingerprint)
