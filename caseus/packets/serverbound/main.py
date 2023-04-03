r"""Serverbound :class:`~.Packet`\s."""

import pak

from public import public

from ..common import (
    _NestedLegacyType,
    _NestedTribulleType,
    _NestedExtensionType,
    _SimpleNestedPacketType,
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
class ObjectSyncPacket(ServerboundPacket):
    id = (4, 3)

    round_id: types.Int
    objects:  types.ObjectDescription(serverbound=True)[None]

@public
class PlayerMovementPacket(ServerboundPacket):
    id = (4, 4)

    round_id:            types.Int
    moving_right:        types.Boolean
    moving_left:         types.Boolean
    x:                   pak.ScaledInteger(types.Int,   100 / 30)
    y:                   pak.ScaledInteger(types.Int,   100 / 30)
    velocity_x:          pak.ScaledInteger(types.Short, 10)
    velocity_y:          pak.ScaledInteger(types.Short, 10)
    jumping:             types.Boolean
    jumping_frame_index: types.Byte
    entered_portal:      pak.Enum(types.Byte, enums.Portal)

    # Only present if transformed or rolling.
    rotation_info: pak.Optional(
        pak.Compound(
            "RotationInfo",

            rotation         = pak.ScaledInteger(types.Short, 100),
            angular_velocity = pak.ScaledInteger(types.Short, 100),
            fixed_rotation   = types.Boolean,
        )
    )

@public
class PlayerDiedPacket(ServerboundPacket):
    id = (4, 5)

    round_id: types.Int
    type:     pak.Enum(types.UnsignedByte, enums.DeathType)

@public
class SetFacingPacket(ServerboundPacket):
    # NOTE: I don't think this is ever sent by the game.

    id = (4, 6)

    facing_right: types.ByteBoolean

@public
class PlayerActionPacket(ServerboundPacket):
    id = (4, 9)

    animation: pak.Enum(types.Byte, enums.PlayerAction)

@public
class CreateShamanLabelPacket(ServerboundPacket):
    """Sent to the satellite server to create a shaman label.

    .. note::

        If sent to the server when not shaman, you will be kicked.
    """

    id = (5, 9)

    label: pak.Enum(types.Byte, enums.ShamanLabel)
    x:     types.Short
    y:     types.Short

@public
class RemoveObjectPacket(ServerboundPacket):
    id = (5, 15)

    object_id: types.Int

@public
class EnterHolePacket(ServerboundPacket):
    id = (5, 18)

    hole_type: pak.Enum(types.Byte, enums.HoleType)
    round_id:  types.Int
    map_code:  types.Int

    distance_from_nearest_hole: pak.ScaledInteger(types.UnsignedShort, 30)

    x: types.Short
    y: types.Short

@public
class GetCheesePacket(ServerboundPacket):
    id = (5, 19)

    round_id:     types.Int
    x:            types.Short
    y:            types.Short
    cheese_index: types.UnsignedByte
    context_id:   types.UnsignedByte

    distance_from_nearest_cheese: pak.ScaledInteger(types.UnsignedShort, 30)

@public
class AddShamanObjectPacket(ServerboundPacket):
    id = (5, 20)

    round_id:          types.Byte
    object_id:         types.LimitedLEB128
    shaman_object_id:  types.LimitedLEB128
    x:                 types.LimitedLEB128
    y:                 types.LimitedLEB128
    angle:             types.LimitedLEB128
    velocity_x:        types.LimitedLEB128
    velocity_y:        types.LimitedLEB128
    mice_collidable:   types.Boolean
    spawned_by_player: types.ByteBoolean
    session_id:        types.LimitedLEB128

@public
class UseIceCubePacket(ServerboundPacket):
    id = (5, 21)

    session_id: types.Int
    x:          types.Short
    y:          types.Short

@public
class CollectBonusPointPacket(ServerboundPacket):
    id = (5, 25)

    bonus_id: types.Int

@public
class SetWorldGravityPacket(ServerboundPacket):
    id = (5, 28)

    x: types.Short
    y: types.Short

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
class RoomPasswordPacket(ServerboundPacket):
    id = (5, 39)

    password:  types.String
    room_name: types.String

@public
class RoomMessagePacket(ServerboundPacket):
    id = (6, 6)

    CIPHER = XOR

    message: types.String

@public
class StaffMessagePacket(ServerboundPacket):
    id = (6, 10)

    message_type: pak.Enum(types.Byte, enums.StaffMessageType)
    message:      types.String

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
class PlayEmotePacket(ServerboundPacket):
    id = (8, 1)

    emote:              pak.Enum(types.Byte, enums.Emote)
    partner_session_id: types.Int
    argument:           pak.Optional(types.String)

    @property
    def is_multi(self):
        return self.partner_session_id != -1

@public
class ShowEmoticonPacket(ServerboundPacket):
    id = (8, 5)

    emoticon: pak.Enum(types.Byte, enums.Emoticon)

@public
class CollectEasterEggPacket(ServerboundPacket):
    id = (8, 6)

@public
class MeepPacket(ServerboundPacket):
    id = (8, 39)

    x: types.LimitedLEB128
    y: types.LimitedLEB128

@public
class GetCollectiblePacket(ServerboundPacket):
    id = (8, 43)

    round_id:      types.Byte
    adventure_id:  types.UnsignedByte
    individual_id: types.UnsignedShort
    x:             types.Short
    y:             types.Short

@public
class EnterAdventureAreaPacket(ServerboundPacket):
    id = (8, 44)

    adventure_id: types.UnsignedByte
    area_id:      types.UnsignedShort

@public
class SetIceCubePacket(ServerboundPacket):
    id = (8, 45)

    # Only ever sent with 'Unfreeze' and '0' as 'action' and 'seconds'.

    action:  pak.Enum(types.Byte, enums.IceCubeAction)
    seconds: types.Short

@public
class VampireInfectPacket(ServerboundPacket):
    id = (8, 66)

    session_id: types.Int

@public
class EnterTribeHousePacket(ServerboundPacket):
    id = (16, 1)

@public
class AdventureActionPacket(ServerboundPacket):
    id = (16, 10)

    adventure_id: types.UnsignedByte
    action_id:    types.UnsignedByte
    arguments:    types.String[types.UnsignedByte]

    def int_argument(self, index):
        return int(self.arguments[index])

    def str_argument(self, index):
        return self.arguments[index]

    def bool_argument(self, index):
        return self.arguments[index] == "true"

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

    # Seems to have something do with registering an account.
    # Maybe the previously tried username?
    unk_string_8: types.String

@public
class HitMonsterPacket(ServerboundPacket):
    id = (26, 5)

    monster_id: types.Int
    push_right: types.ByteBoolean

@public
class PlayerAttackPacket(ServerboundPacket):
    id = (26, 9)

@public
class MonsterSyncPacket(ServerboundPacket):
    id = (26, 10)

    monsters: pak.Compound(
        "MonsterInfo",

        monster_id = types.Int,
        x          = types.Int,
        y          = types.Int,
    )[types.UnsignedShort]

@public
class PlayerDamagedPacket(ServerboundPacket):
    id = (26, 11)

@public
class SteamInfoPacket(ServerboundPacket):
    id = (26, 12)

    user_id:      types.String
    empty_string: types.String

@public
class IPSPingPacket(ServerboundPacket):
    """A packet to test the ping of the satellite server.

    Most staff roles are able to get ping information in
    their ``/ips`` screen. When doing so, this is the packet
    that the client sends to the satellite server, expecting a
    :class:`clientbound.IPSPongPacket <.IPSPongPacket>` in return.
    If it does not get one within 10 seconds, then it gives up
    trying to ping. If it does get one however, it will send
    another one, and another, and so on.

    If the server does not think you should be able to ping,
    then it will just ignore this packet.
    """

    id = (26, 25)

@public
class KeepAlivePacket(ServerboundPacket):
    """Sent by the client periodically to keep the :class:`~.Connection` alive."""

    id = (26, 26)

@public
class SetTransformationPacket(ServerboundPacket):
    id = (27, 11)

    transformation: pak.Enum(types.Short, enums.Transformation)

@public
class HandshakePacket(ServerboundPacket):
    """Sent by the client to start the connection."""

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

    # How the client got referred the game. If not a
    # value from the 'ReferralID' enum, then the value
    # is a player's global id from the old referral system.
    referee: pak.EnumOr(types.Int, enums.RefereeID)

    milliseconds_since_start: types.Int

    # Set by 'x_defNomJeuModule801', but is never set by Transformice,
    # and so it is always empty.
    game_name: types.String

@public
class PongPacket(ServerboundPacket):
    id = (28, 6)

    payload: types.Byte

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
class LuaScriptPacket(ServerboundPacket):
    id = (29, 1)

    script: types.LargeString

@public
class KeyboardPacket(ServerboundPacket):
    CIPHER = XOR

    id = (29, 2)

    key_code:   types.LimitedLEB128
    down:       types.Boolean
    x:          types.LimitedLEB128
    y:          types.LimitedLEB128
    velocity_x: pak.ScaledInteger(types.LimitedLEB128, 10)
    velocity_y: pak.ScaledInteger(types.LimitedLEB128, 10)

@public
class MouseDownPacket(ServerboundPacket):
    id = (29, 3)

    x: types.LimitedLEB128
    y: types.LimitedLEB128

@public
class PickColorPacket(ServerboundPacket):
    id = (29, 32)

    color_picker_id: types.Int
    color:           types.Int

@public
class OpenInventoryPacket(ServerboundPacket):
    id = (31, 1)

@public
class UseItemPacket(ServerboundPacket):
    id = (31, 3)

    item_id: types.Short

@public
class SetEquippedItemPacket(ServerboundPacket):
    id = (31, 4)

    item_id:  types.Short
    equipped: types.Boolean

@public
class TradeInvitePacket(ServerboundPacket):
    id = (31, 5)

    # NOTE: This packet is also used for
    # accepting a trade invitiation.

    username: types.String

@public
class CancelTradePacket(ServerboundPacket):
    id = (31, 6)

    username:       types.String
    because_shaman: types.Boolean

@public
class UpdateTradeContentsPacket(ServerboundPacket):
    id = (31, 8)

    item_id:  types.Short
    increase: types.Boolean
    several:  types.Boolean

@public
class TradeLockPacket(ServerboundPacket):
    id = (31, 9)

    locked: types.Boolean

@public
class SatelliteDelayedIdentificationPacket(ServerboundPacket):
    """Sent by the client to the satellite server after switching to it."""

    id = (44, 1)

    timestamp: types.Int
    global_id: types.Int
    auth_id:   types.Int

@public
class TribulleWrapperPacket(ServerboundPacket):
    id = (60, 3)

    CIPHER = XOR

    nested: _NestedTribulleType(ServerboundTribullePacket)

@public
class ShamanObjectPreviewPacket(ServerboundPacket):
    id = (100, 2)

    shaman_object_id: types.LimitedLEB128
    x:                types.LimitedLEB128
    y:                types.LimitedLEB128

    # If a rock with children, then the first child's angle.
    # Else the object's angle.
    angle: types.LimitedLEB128

    # Only non-empty if it's a rock.
    # Has format like '2;3,4;5,6' where '2' is the number
    # of children, and then each semicolon-separated pair
    # of numbers is the x,y offset within the parent coordinate
    # system.
    child_offsets: types.String

    is_spawning: types.Boolean

@public
class RemoveShamanObjectPreviewPacket(ServerboundPacket):
    id = (100, 3)

@public
class VisualConsumableInfoPacket(ServerboundPacket):
    id = (100, 40)

    class _InfoPacket(pak.Packet):
        class Header(pak.Packet.Header):
            id: types.UnsignedByte

    class PaintLine(_InfoPacket):
        id = 2

        start_x: pak.ScaledInteger(types.Int, 10)
        start_y: pak.ScaledInteger(types.Int, 10)
        end_x:   pak.ScaledInteger(types.Int, 10)
        end_y:   pak.ScaledInteger(types.Int, 10)

    class RemovePaint(_InfoPacket):
        id = 3

        # Normally only sent by those with the
        # 'Arbitre' and 'Modo' staff roles. They
        # can hold the CTRL key while clicking on
        # someone's painting to send this packet.

        artist_name: types.String

    info: _SimpleNestedPacketType(_InfoPacket)

@public
class InteractWithOfficialNPCPacket(ServerboundPacket):
    id = (100, 75)

    class _Interaction(pak.Packet):
        class Header(pak.Packet.Header):
            id: types.Byte

    class ClickNPC(_Interaction):
        id = 4

        name: types.String

    class PurchaseItem(_Interaction):
        id = 10

        item_index: types.UnsignedByte

    class _InteractionType(pak.Type):
        @classmethod
        def _unpack(cls, buf, *, ctx):
            header     = InteractWithOfficialNPCPacket._Interaction.Header.unpack(buf)
            packet_cls = InteractWithOfficialNPCPacket._Interaction.subclass_with_id(header.id)

            return packet_cls.unpack(buf)

        @classmethod
        def _pack(cls, value, *, ctx):
            return value.pack()

    interaction: _InteractionType

@public
class CheesesAndHolesSyncPacket(ServerboundPacket):
    id = (100, 80)

    class _Cheeses(pak.Type):
        _default = []

        elem_type = pak.Compound(
            "CheeseInfo",

            x = types.Short,
            y = types.Short,
        )

        @classmethod
        def _unpack(cls, buf, *, ctx):
            length = types.UnsignedByte.unpack(buf, ctx=ctx) // 2

            return [cls.elem_type.unpack(buf, ctx=ctx) for _ in range(length)]

        @classmethod
        def _pack(cls, value, *, ctx):
            length = len(value) * 2

            return (
                types.UnsignedByte.pack(length, ctx=ctx) +

                b"".join(cls.elem_type.pack(x, ctx=ctx) for x in value)
            )

    class _Holes(pak.Type):
        _default = []

        elem_type = pak.Compound(
            "HoleInfo",

            type = pak.Enum(types.Short, enums.HoleType),

            x = types.Short,
            y = types.Short,
        )

        @classmethod
        def _unpack(cls, buf, *, ctx):
            length = types.UnsignedByte.unpack(buf, ctx=ctx) // 3

            return [cls.elem_type.unpack(buf, ctx=ctx) for _ in range(length)]

        @classmethod
        def _pack(cls, value, *, ctx):
            length = len(value) * 3

            return (
                types.UnsignedByte.pack(length, ctx=ctx) +

                b"".join(cls.elem_type.pack(x, ctx=ctx) for x in value)
            )

    cheeses: _Cheeses
    holes:   _Holes

@public
class OpenFashionSquadOutfitsMenuPacket(ServerboundPacket):
    id = (149, 12)

@public
class AddFashionSquadOutfitPacket(ServerboundPacket):
    id = (149, 13)

    outfit_name: types.String
    background:  pak.EnumOr(types.Short, enums.FashionSquadOutfitBackground)
    date:        types.String
    outfit_code: types.String # TODO: Parse outfit.

@public
class RemoveFashionSquadOutfitPacket(ServerboundPacket):
    id = (149, 14)

    outfit_id: types.Int

@public
class OpenFashionSquadSalesMenuPacket(ServerboundPacket):
    id = (149, 16)

@public
class RemoveFashionSquadSalePacket(ServerboundPacket):
    id = (149, 17)

    sale_id: types.Int

@public
class AddFashionSquadSalePacket(ServerboundPacket):
    id = (149, 18)

    item_id:       types.String
    starting_date: types.String
    ending_date:   types.String
    percentage:    types.Byte

@public
class InteractWithLuaNPCPacket(ServerboundPacket):
    id = (149, 20)

    name: types.String

@public
class SetLanguagePacket(ServerboundPacket):
    id = (176, 1)

    language: types.String

@public
class ClientVerificationPacket(ServerboundPacket):
    id = (176, 47)

    # There really isn't a good way to handle
    # the contents of this packet because it is
    # ciphered with a key that depends on a previous
    # clientbound 'ClientVerificationPacket' and
    # furthermore its format changes like other
    # game secrets do.
    #
    # So to deal with this, we just have a single
    # bytearray field to hold all the ciphered data.
    ciphered_data: pak.RawByte[None]

@public
class ExtensionWrapperPacket(ServerboundPacket):
    # This ID doesn't seem to be used at all.
    id = (255, 255)

    nested: _NestedExtensionType(ServerboundExtensionPacket)
