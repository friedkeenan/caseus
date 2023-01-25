r"""Serverbound :class:`~.Packet`\s."""

import pak

from public import public

from ..common import (
    _NestedLegacyType,
    _NestedTribulleType,
    _NestedExtensionType,
)

from ..packet import (
    ServerboundPacket,
    ServerboundTribullePacket,
    ServerboundLegacyPacket,
    ServerboundExtensionPacket,
)

from ...secrets import IDENTIFICATION, XOR

from ... import enums
from ... import types

@public
class LegacyWrapperPacket(ServerboundPacket):
    id = (1, 1)

    nested: _NestedLegacyType(ServerboundLegacyPacket)

@public
class CreateShamanLabel(ServerboundPacket):
    """Sent to the satellite server to create a shaman label.

    .. note::

        If sent to the server when not shaman, you will be kicked.
    """

    id = (5, 9)

    label: pak.Enum(types.Byte, enums.ShamanLabel)
    x:     types.Short
    y:     types.Short

@public
class JoinRoomPacket(ServerboundPacket):
    id = (5, 38)

    # Only non-empty when choosing a room from the room list menu.
    community: types.String

    # The server will strip any illegal characters
    # from the name, for instance you cannot join
    # the room "*\x03TribeName" using this packet,
    # as you will instead be put in "*TribeName".
    name: types.String

    # True if using the 'salonauto' command.
    auto: types.Boolean

    # NOTE: The game has code for adding more data
    # onto this packet, however it is never used.

@public
class RoomMessagePacket(ServerboundPacket):
    id = (6, 6)

    CIPHER = XOR

    message: types.String

@public
class CommandPacket(ServerboundPacket):
    """Sent to the server when certain commands are used.

    .. note::

        Not all commands end up sending this packet,
        and some commands are sent to only the main
        server, some to only the satellite server,
        and some to both.
    """

    id = (6, 26)

    CIPHER = XOR

    # The command without the '/' prefix.
    command: types.String

@public
class EnvironmentUserIdPacket(ServerboundPacket):
    id = (26, 12)

    # This seems to always be the player's Steam ID.
    user_id: types.String

    # Seems to always be empty.
    unk_string_2: types.String

@public
class KeepAlivePacket(ServerboundPacket):
    """Sent by the client periodically to keep the :class:`~.Connection` alive."""

    id = (26, 26)

@public
class HandshakePacket(ServerboundPacket):
    """Sent by the client to start the :class:`~.Connection`."""

    id = (28, 1)

    game_version: types.Short
    language:     types.String

    # Random hardcoded string, changed in the game's source routinely.
    connection_token: types.String

    player_type: types.String

    # Uses javascript to get 'navigator.appVersion' and 'navigator.appName'
    # and combines them with a '-' in between. If it can't execute javascript
    # then it just sends a single '-'.
    browser_info: types.String

    # The length of the loaded bytes of the
    # loader SWF. If the server does not
    # receive the expected size, it ends
    # the connection.
    loader_stage_size: types.Int

    # SharedObject for "Transformice" accessing "ccf" data.
    # Set by clientbound packet (26, 28), if not set then empty.
    # Seemingly always unset.
    ccf_data: types.String

    concatenated_font_name_hash: types.String

    # Unescaped 'Capabilities.serverString'.
    server_string: types.String

    # Seemingly random hardcoded number set to different values
    # depending on a bunch of stuff. Seemingly always 0 though.
    unk_int_10: types.Int

    milliseconds_since_start: types.Int

    # Set by 'x_defNomJeuModule801', but is never set by Transformice,
    # and so it is always empty.
    game_name: types.String

@public
class LoginPacket(ServerboundPacket):
    id = (26, 8)

    CIPHER = IDENTIFICATION

    username: types.String

    # An empty string when logging in as a guest.
    password_hash: types.String
    loader_url:    types.String
    start_room:    types.String

    ciphered_auth_token: types.Int

    # Hardcoded as '18' in game.
    unk_short_6: types.Short

    login_method: pak.Enum(types.Byte, enums.LoginMethod)

    # Has something to do with the username it looks like.
    unk_string_8: types.String

@public
class SystemInformationPacket(ServerboundPacket):
    """Sent by the client in response to :class:`.clientbound.HandshakeResponsePacket`."""

    id = (28, 17)

    # Set to 'Capabilities.language'.
    language: types.String

    # Set to 'Capabilities.os'.
    os: types.String

    # Set to 'Capabilities.version'.
    flash_version: types.String

    # Always written as '0'.
    zero_byte: types.Byte

@public
class SatelliteHandshakePacket(ServerboundPacket):
    """Sent by the client to the satellite server after switching to it."""

    id = (44, 1)

    timestamp: types.Int
    global_id: types.Int
    auth_id:   types.Int

@public
class TribulleWrapperPacket(ServerboundPacket):
    id = (60, 3)

    nested: _NestedTribulleType(ServerboundTribullePacket)

@public
class ClientLanguagePacket(ServerboundPacket):
    id = (176, 1)

    code: types.String

@public
class ExtensionWrapperPacket(ServerboundPacket):
    # This ID doesn't seem to be used at all.
    id = (255, 255)

    nested: _NestedExtensionType(ServerboundExtensionPacket)
