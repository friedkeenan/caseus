r"""Clientbound :class:`~.Packet`\s."""

# TODO: Split this file up. Seriously.

import dataclasses
import pak

from public import public

from ..common import (
    _NestedLegacyType,
    _NestedTribulleType,
    _NestedExtensionType,
    _SimpleNestedPacketType,
)

from ..packet import (
    ClientboundPacket,
    ClientboundTribullePacket,
    ClientboundLegacyPacket,
    ClientboundExtensionPacket,
)

from ... import types
from ... import enums
from ... import game

@public
class LegacyWrapperPacket(ClientboundPacket):
    id = (1, 1)

    nested: _NestedLegacyType(ClientboundLegacyPacket)

@public
class ObjectSyncPacket(ClientboundPacket):
    id = (4, 3)

    objects: types.ObjectDescription(serverbound=False)[None]

@public
class PlayerMovementPacket(ClientboundPacket):
    id = (4, 4)

    session_id:          types.Int
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

    # Only present if transformed.
    rotation_info: pak.Optional(
        pak.Compound(
            "RotationInfo",

            rotation         = pak.ScaledInteger(types.Short, 100),
            angular_velocity = pak.ScaledInteger(types.Short, 100),
            fixed_rotation   = types.Boolean
        )
    )

@public
class SetFacingPacket(ClientboundPacket):
    id = (4, 6)

    session_id:   types.Int
    facing_right: types.ByteBoolean

@public
class SetOtherFacingPacket(ClientboundPacket):
    id = (4, 10)

    # NOTE: Unlike 'SetFacingPacket', this
    # packet will have no effect on the player
    # that the client controls.

    session_id:   types.Int
    facing_right: types.ByteBoolean

@public
class NewRoundPacket(ClientboundPacket):
    id = (5, 2)

    map_code:    types.Int
    num_players: types.Short
    round_id:    types.Byte
    xml:         types.CompressedString
    author:      types.String

    # NOTE: We use 'EnumOr' to make sure we preserve whatever value
    # the server sends the client. Normally this would be handled with
    # a fallback value implemented in the enum class, but in particular
    # for archival purposes, it is important to me to preserve the original
    # value of the category, even if the client doesn't care about it.
    category: pak.EnumOr(types.Byte, enums.MapCategory)

    mirrored:        types.Boolean
    has_conjuration: types.Boolean
    has_collision:   types.Boolean

    # Never actually has an effect because
    # the game only checks the variable this
    # gets assigned to if it receives a
    # 'SetCollisionDamagePacket', which overrides
    # the variable this gets set to.
    #
    # It's really weird.
    has_collision_damage: types.Boolean

    # If '0' then ignored.
    player_mass_percentage: types.Int

    # Not always present, and the game does
    # not parse any extra data at all, but
    # has code for if there simply *is*
    # extra data.
    extra_data: pak.RawByte[None]

    @property
    def vanilla_overrides_category(self):
        return (
            len(self.xml) == 0 or

            len(self.extra_data) > 0 or

            (
                len(self.author) == 0       or
                self.author.startswith("_") or
                self.author.startswith("~")
            ) or

            # The value for the category is not one the game knows about.
            not isinstance(self.category, enums.MapCategory) or

            self.category.overridden_by_vanilla
        )

@public
class CreateShamanLabelPacket(ClientboundPacket):
    """Sent by the satellite server to create a shaman label."""

    id = (5, 9)

    label: pak.Enum(types.Byte, enums.ShamanLabel)
    x:     types.Short
    y:     types.Short

@public
class AddBonusPacket(ClientboundPacket):
    id = (5, 14)

    x:        types.LimitedLEB128
    y:        types.LimitedLEB128
    bonus:    pak.Enum(types.LimitedLEB128, enums.Bonus)
    angle:    types.LimitedLEB128
    bonus_id: types.LimitedLEB128
    visible:  types.ByteBoolean

@public
class RemoveObjectPacket(ClientboundPacket):
    id = (5, 15)

    object_id: types.Int

@public
class AddShamanObjectPacket(ClientboundPacket):
    id = (5, 20)

    object_id:        types.Int # If '-1' then automatically assigned.
    shaman_object_id: types.LimitedLEB128
    x:                types.LimitedLEB128
    y:                types.LimitedLEB128
    angle:            pak.ScaledInteger(types.LimitedLEB128, 100)
    velocity_x:       pak.ScaledInteger(types.LimitedLEB128, 100)
    velocity_y:       pak.ScaledInteger(types.LimitedLEB128, 100)
    mice_collidable:  types.ByteBoolean
    colors:           types.Int[types.Byte]

@public
class JoinedRoomPacket(ClientboundPacket):
    id = (5, 21)

    official:  types.Boolean
    raw_name:  types.String
    flag_code: types.String

    def room(self):
        return game.Room(
            official  = self.official,
            raw_name  = self.raw_name,
            flag_code = self.flag_code,
        )

@public
class SetRoundTimerPacket(ClientboundPacket):
    id = (5, 22)

    seconds: types.Short

@public
class SetSnowingPacket(ClientboundPacket):
    id = (5, 23)

    snowing:        types.ByteBoolean
    snowball_power: types.Short

@public
class SetWorldGravityPacket(ClientboundPacket):
    id = (5, 28)

    # When this is positive, after the
    # specified time, the client will
    # send a 'SetWorldGravityPacket' to
    # the server with the previous gravity
    # information to set it back to normal.
    #
    # This is used for the 'Gravitational'
    # shaman skill.
    milliseconds: types.Int

    x: pak.ScaledInteger(types.Int, 1000)
    y: pak.ScaledInteger(types.Int, 1000)

@public
class SetPlayerSizePacket(ClientboundPacket):
    id = (5, 31)

    session_id:     types.Int
    percentage:     types.UnsignedShort
    exclude_shaman: types.Boolean

@public
class FreezePacket(ClientboundPacket):
    id = (5, 34)

    session_id: types.Int
    freeze:     types.Boolean
    show_ice:   types.Boolean

@public
class AddSpidermouseWebPacket(ClientboundPacket):
    id = (5, 36)

    x: types.Short
    y: types.Short

@public
class RoomPasswordPacket(ClientboundPacket):
    id = (5, 39)

    room_name: types.String

@public
class EventMapActionPacket(ClientboundPacket):
    id = (5, 44)

    # Only certain actions are available baased on
    # the event type seemingly set in the 'S'
    # attribute of the "settings" element of the
    # map XML when the map author is 'Tigrounette'
    # or 'Transformice' or starts with '_'.
    action: pak.Enum(types.Short, enums.EventMapAction)

@public
class SetIndianaMousePacket(ClientboundPacket):
    id = (5, 46)

    # NOTE: This only actually works if a
    # static const boolean in the game is
    # true (which it is not), and the author
    # of the current map is '_Museum' or '_peche'.

    session_id: types.Int
    enabled:    types.Boolean

    @property
    def all_players(self):
        return self.session_id == -1

@public
class AddTrapPacket(ClientboundPacket):
    id = (5, 47)

    trap:              pak.Enum(types.Short, enums.Trap)
    x:                 types.Short
    y:                 types.Short
    width_percentage:  types.Short
    height_percentage: types.Short
    angle:             types.Short

@public
class SpawnStaticParticlePacket(ClientboundPacket):
    id = (5, 50)

    particle_id: types.Byte
    x:           types.Short
    y:           types.Short

@public
class AddCollectablePacket(ClientboundPacket):
    id = (5, 51)

    adventure_id:   types.UnsignedByte
    individual_id:  types.UnsignedShort # TODO: Better name?
    collectable_id: types.UnsignedByte
    x:              types.Short
    y:              types.Short

@public
class AddAdventureAreaPacket(ClientboundPacket):
    # TODO: I am not happy with this name.

    id = (5, 54)

    adventure_id: types.UnsignedByte
    area_id:      types.UnsignedShort # NOTE: Should not be '0'.
    x:            types.Short
    y:            types.Short
    width:        types.UnsignedShort
    height:       types.UnsignedShort

@public
class RoomMessagePacket(ClientboundPacket):
    id = (6, 6)

    username: types.String
    message:  types.String

    # Seems to always be 'False', and the value
    # doesn't seem to matter in the game code.
    unk_boolean_3: types.Boolean

@public
class OldTribeMessagePacket(ClientboundPacket):
    id = (6, 8)

    message:  types.String
    username: types.String

    @property
    def should_display(self):
        return "<" not in self.message

    @property
    def has_username(self):
        return len(self.event) > 0

@public
class GeneralMessagePacket(ClientboundPacket):
    id = (6, 9)

    message: types.String

    @property
    def should_display(self):
        return not (
            "<img" in self.message or
            "<a"   in self.message
        )

@public
class StaffMessagePacket(ClientboundPacket):
    id = (6, 10)

    message_type: pak.Enum(types.Byte, enums.StaffMessageType)

    # NOTE: Not always used, and not always just a username.
    name: types.String

    message: types.String

    # Whether or not message decorating should be disabled.
    # If it is disabled, then the message will just show up
    # in the general channel with no frill besides being colored.
    # If decoration is disabled for the 'ModeratorRoom' and
    # 'ModeratorCommunity' message types, then nothing is displayed.
    disable_decoration: types.Boolean

    # If 'True' then 'message' is treated as a translation key.
    is_translation: types.Boolean

    translation_args: types.String[types.Byte]

@public
class ServerMessagePacket(ClientboundPacket):
    id = (6, 20)

    general_channel: types.Boolean

    # If the translation key does not start with
    # '$', or has a space, or has a newline, then
    # it is just treated as the final message.
    translation_key:  types.String
    translation_args: types.String[types.Byte]

@public
class PlayEmotePacket(ClientboundPacket):
    id = (8, 1)

    session_id: types.Int
    emote:      pak.Enum(types.Byte, enums.Emote)
    argument:   pak.Optional(types.String, lambda packet: packet.emote is enums.Emote.Flag)
    from_lua:   types.Boolean

@public
class GainCurrencyNotificationPacket(ClientboundPacket):
    id = (8, 2)

    currency: pak.Enum(types.Byte, enums.Currency)
    quantity: types.Byte

@public
class MovePlayerPacket(ClientboundPacket):
    id = (8, 3)

    IGNORE = pak.util.UniqueSentinel("IGNORE")

    class _Velocity(pak.Type):
        IGNORE_VALUE = -9998

        @classmethod
        def _default(cls, *, ctx):
            return MovePlayerPacket.IGNORE

        @classmethod
        def _unpack(cls, buf, *, ctx):
            value = types.LimitedLEB128.unpack(buf, ctx=ctx)
            if value == cls.IGNORE_VALUE:
                return MovePlayerPacket.IGNORE

            return value / 10

        @classmethod
        def _pack(cls, value, *, ctx):
            if value is MovePlayerPacket.IGNORE:
                value = cls.IGNORE_VALUE
            else:
                value = int(value * 10)

            return types.LimitedLEB128.pack(value, ctx=ctx)

    x:                 types.LimitedLEB128
    y:                 types.LimitedLEB128
    position_relative: types.ByteBoolean
    velocity_x:        _Velocity
    velocity_y:        _Velocity
    velocity_relative: types.ByteBoolean

@public
class ShowEmoticonPacket(ClientboundPacket):
    id = (8, 5)

    session_id: types.Int
    emoticon:   pak.Enum(types.Byte, enums.Emoticon)

@public
class PlayerVictoryPacket(ClientboundPacket):
    id = (8, 6)

    type:         pak.Enum(types.Byte, enums.VictoryType)
    session_id:   types.Int
    score:        types.Short
    place:        types.Byte
    centiseconds: types.UnsignedShort

@public
class SetPlayerScorePacket(ClientboundPacket):
    id = (8, 7)

    session_id: types.Int
    score:      types.Short

@public
class EarnExperiencePacket(ClientboundPacket):
    id = (8, 9)

    quantity: types.Int

@public
class EnableSkillPacket(ClientboundPacket):
    id = (8, 10)

    skill_id: types.UnsignedByte
    argument: types.UnsignedByte

@public
class ShamanInfoPacket(ClientboundPacket):
    id = (8, 11)

    blue_session_id:     types.Int
    pink_session_id:     types.Int
    blue_shaman_mode:    pak.Enum(types.Byte, enums.ShamanMode)
    pink_shaman_mode:    pak.Enum(types.Byte, enums.ShamanMode)
    blue_level:          types.UnsignedShort
    pink_level:          types.UnsignedShort
    blue_cartouche_id:   types.Short
    pink_cartouche_id:   types.Short
    blue_without_skills: types.Boolean
    pink_without_skills: types.Boolean

@public
class SetShamanPacket(ClientboundPacket):
    id = (8, 12)

    session_id:         types.Int
    shaman_mode:        pak.Enum(types.Byte, enums.ShamanMode)
    level:              types.Short
    cartouche_id:       types.UnsignedShort
    without_skills:     types.Boolean
    starting_object_id: types.Int

@public
class BasePlayerInformationPacket(ClientboundPacket):
    username:          types.String
    global_id:         types.Int
    registration_time: types.Int
    staff_role:        pak.Enum(types.Byte, enums.StaffRole)
    gender:            pak.Enum(types.Byte, enums.Gender)
    tribe_name:        types.String
    soulmate:          types.String

@public
class PlayerProfilePacket(BasePlayerInformationPacket):
    id = (8, 16)

    class _Badges(pak.Type):
        _default = []

        elem_type = pak.Compound(
            "BadgeInfo",

            badge_id = types.UnsignedShort,
            quantity = types.UnsignedShort,
        )

        @classmethod
        def _unpack(cls, buf, *, ctx):
            length = types.UnsignedShort.unpack(buf, ctx=ctx) // 2

            return [cls.elem_type.unpack(buf, ctx=ctx) for _ in range(length)]

        @classmethod
        def _pack(cls, value, *, ctx):
            length = len(value) * 2

            return (
                types.UnsignedShort.pack(length, ctx=ctx) +

                b"".join(cls.elem_type.pack(x, ctx=ctx) for x in value)
            )

    # NOTE: The game stores these as a vector
    # but manually reads each out. This is likely
    # done to be symmetric with the stats in
    # the 'OldNekodancerProfilePacket'.
    normal_saves:                types.Int
    shaman_cheese:               types.Int
    firsts:                      types.Int
    cheese:                      types.Int
    hard_saves:                  types.Int
    completed_bootcamps:         types.Int
    divine_saves:                types.Int
    normal_saves_without_skills: types.Int
    hard_saves_without_skills:   types.Int
    divine_saves_without_skills: types.Int

    title_id: types.Short

    unlocked_titles: pak.Compound(
        "TitleInfo",

        title_id = types.Short,
        stars    = types.Byte,
    )[types.Short]

    outfit_code: types.String # TODO: Parse outfit.
    level:       types.Short
    badges:      _Badges

    gamemode_stats: pak.Compound(
        "GamemodeStatInfo",

        stat_id           = types.UnsignedByte,
        quantity          = types.Int,
        needed_quantity   = types.Int,
        unlocked_badge_id = types.Short,
    )[types.Byte]

    cartouche_id:             types.UnsignedByte
    cartouche_id_list:        types.UnsignedByte[types.UnsignedByte]
    display_adventure_points: types.Boolean
    adventure_points:         types.Int

@public
class OldNekodancerProfilePacket(BasePlayerInformationPacket):
    id = (8, 17)

    stats: pak.Compound(
        "StatInfo",

        stat_id  = types.Byte,
        quantity = types.Int,
    )[types.Byte]

    # NOTE: Not used in Transformice
    # or technically Nekodancer, but
    # is named the same as the profile
    # packet that Nekodancer *does* use
    # where it is the fur ID.
    fur_id: types.Byte

    # Not used anywhere either in Transformice or
    # Nekodancer. Probably other outfit elements,
    # perhaps shirt and pants?
    unk_byte_3: types.Byte
    unk_byte_4: types.Byte

@public
class AddNPCPacket(ClientboundPacket):
    id = (8, 30)

    session_id:       types.Int
    name:             types.String
    title_id:         types.Short
    feminine:         types.Boolean
    outfit_code:      types.String # TODO: Parse outfit.
    x:                types.LimitedLEB128
    y:                types.LimitedLEB128
    facing_right:     types.Boolean
    face_player:      types.Boolean
    interface:        pak.Enum(types.Byte, enums.NPCInterface)
    periodic_message: types.String

@public
class MeepExplosionPacket(ClientboundPacket):
    id = (8, 38)

    session_id: types.Int
    x:          types.Short
    y:          types.Short
    power:      types.Int

@public
class SetCanMeepPacket(ClientboundPacket):
    id = (8, 39)

    enabled: types.Boolean

@public
class SetIceCubePacket(ClientboundPacket):
    id = (8, 45)

    session_id: types.Int
    action:     pak.Enum(types.Byte, enums.IceCubeAction)
    seconds:    types.Short

@public
class SetVampirePacket(ClientboundPacket):
    id = (8, 66)

    session_id: types.Int
    vampire:    types.Boolean

    # Stored globally and not per-player.
    transmissible: types.Boolean

@public
class UpdateAdventuresPacket(ClientboundPacket):
    id = (16, 9)

    adventure_id_list:  types.Byte[types.Byte]
    enable:             types.Boolean
    announce_adventure: types.Boolean

@public
class AdventureActionPacket(ClientboundPacket):
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
class Unknown_20_4_Packet(ClientboundPacket):
    id = (20, 4)

    unk_array_1: pak.Compound(
        "UnknownCompound",

        unk_int_1   = types.Int,
        unk_int_2   = types.Int,
        class_names = types.String[types.Byte],
    )[types.Short]

@public
class LoginSuccessPacket(ClientboundPacket):
    id = (26, 2)

    class CommunityToFlag(pak.Type):
        @classmethod
        def _unpack(cls, buf, *, ctx):
            length = types.UnsignedShort.unpack(buf, ctx=ctx)

            return {
                types.String.unpack(buf, ctx=ctx): types.String.unpack(buf, ctx=ctx)

                for _ in range(length)
            }

        @classmethod
        def _pack(cls, value, *, ctx):
            return (
                types.UnsignedShort.pack(len(value), ctx=ctx) +

                b"".join(
                    types.String.pack(key, ctx=ctx) + types.String.pack(value, ctx=ctx)

                    for key, value in value.items()
                )
            )

    global_id:   types.Int
    username:    types.String
    played_time: types.Int
    community:   pak.Enum(types.Byte, enums.Community)
    session_id:  types.Int

    # Whether you are using a registered account or a guest account.
    registered: types.Boolean

    staff_roles: pak.Enum(types.Byte, enums.StaffRole)[types.Byte]

    # You can also repeat the same message if this is true.
    modo_can_speak_in_all_staff_channels: types.Boolean

    # Never used despite having maybe meaningful values.
    unk_ushort_9: types.UnsignedShort

    community_to_flag: CommunityToFlag

@public
class HandshakeResponsePacket(ClientboundPacket):
    """Sent by the server in response to :class:`.serverbound.HandshakePacket`."""

    id = (26, 3)

    num_online_players: types.Int
    language:           types.String
    country:            types.String
    auth_token:         types.Int

    # If 'True' then the game calls an empty function.
    unk_boolean_5: types.Boolean

@public
class SetPlayerHealthPacket(ClientboundPacket):
    id = (26, 4)

    health: types.Byte

@public
class HitMonsterPacket(ClientboundPacket):
    id = (26, 5)

    monster_id: types.Int
    push_right: types.ByteBoolean

@public
class SpawnMonsterPacket(ClientboundPacket):
    id = (26, 6)

    monster_id: types.Int
    x:          types.Int
    y:          types.Int
    type:       pak.Enum(types.String, enums.Monster)

@public
class RemoveMonsterPacket(ClientboundPacket):
    id = (26, 7)

    monster_id: types.Int

@public
class SetMonsterSpeedPacket(ClientboundPacket):
    id = (26, 8)

    monster_id: types.Int
    speed:      types.Int

@public
class PlayerAttackPacket(ClientboundPacket):
    id = (26, 9)

    session_id: types.Int

@public
class PlayerDamagedPacket(ClientboundPacket):
    id = (26, 11)

    session_id: types.Int

@public
class AccountErrorPacket(ClientboundPacket):
    id = (26, 12)

    # TODO: Enum? Might not be feasible if it
    # has different meanings in different contexts.
    error_code: types.Byte

    unk_string_2: types.String
    unk_string_3: types.String

@public
class IPSPongPacket(ClientboundPacket):
    id = (26, 25)

@public
class OpenNPCShopPacket(ClientboundPacket):
    id = (26, 38)

    name: types.String

    items: pak.Compound(
        "ItemInfo",

        status = pak.Enum(types.UnsignedByte, enums.NPCItemStatus),

        type     = pak.Enum(types.UnsignedByte, enums.NPCItemType),
        id       = types.Int,
        quantity = types.Short,

        # Cost type is always 'NPCItemType.Normal' because you
        # always spend normal items to buy items from an NPC.
        cost_type     = pak.Enum(types.UnsignedByte, enums.NPCItemType),
        cost_id       = types.Int,
        cost_quantity = types.Short,

        hover_translation_key = types.String,
        hover_translation_arg = types.String,
    )[types.UnsignedByte]

@public
class SetCanTransformPacket(ClientboundPacket):
    id = (27, 10)

    can_transform: types.Boolean

@public
class SetTransformationPacket(ClientboundPacket):
    id = (27, 11)

    session_id:     types.Int
    transformation: pak.Enum(types.Short, enums.Transformation)

@public
class LoadAndExecutePacket(ClientboundPacket):
    id = (28, 1)

    swf_data: pak.RawByte[None]

@public
class TranslatedGeneralMessagePacket(ClientboundPacket):
    id = (28, 5)

    # If an empty string, then fallback to the client's
    # selected language. If there is no selected language,
    # then fallback to 'en'.
    #
    # If the client does not have the translations for
    # the language loaded, then it will retrieve them.
    language: types.String

    translation_key:  types.String
    translation_args: types.String[types.Byte]

@public
class PingPacket(ClientboundPacket):
    id = (28, 6)

    payload:     types.Byte
    main_server: types.Boolean

@public
class SetAllowEmailAddressPacket(ClientboundPacket):
    id = (28, 62)

    allow_email: types.Boolean

@public
class ReaffirmServerAddressPacket(ClientboundPacket):
    """Sent to the client to make sure it's connected to the expected server."""

    id = (28, 98)

    address: types.String

@public
class InitializeLuaScriptingPacket(ClientboundPacket):
    id = (29, 1)

@public
class BindKeyboardPacket(ClientboundPacket):
    id = (29, 2)

    key_code: types.Short
    down:     types.ByteBoolean
    active:   types.ByteBoolean

@public
class BindMouseDownPacket(ClientboundPacket):
    id = (29, 3)

    active: types.ByteBoolean

@public
class SetPlayerNameColorPacket(ClientboundPacket):
    id = (29, 4)

    session_id: types.Int
    color:      types.Int

@public
class CleanupLuaScriptingPacket(ClientboundPacket):
    id = (29, 5)

@public
class LuaScriptingLogPacket(ClientboundPacket):
    id = (29, 6)

    message: types.String

@public
class RemoveImagePacket(ClientboundPacket):
    id = (29, 18)

    image_id: types.Int
    fade_out: types.Boolean

@public
class AddImagePacket(ClientboundPacket):
    id = (29, 19)

    image_id:    types.Int
    image_name:  types.String
    target_type: pak.Enum(types.Byte, enums.ImageTargetType)
    target:      types.Int
    x:           types.Int
    y:           types.Int
    scale_x:     types.Float
    scale_y:     types.Float
    rotation:    types.Float
    alpha:       types.Float
    anchor_x:    types.Float
    anchor_y:    types.Float
    fade_in:     types.Boolean

    @property
    def image_url(self):
        if self.image_name == "test":
            return "https://images.atelier801.com/ArmorGame.png"

        if self.image_name.startswith("discord@"):
            return f"https://media.discordapp.net/attachments/{self.image_name.remove_prefix('discord@')}"

        if len(self.image_name) > 12:
            return f"http://images.atelier801.com/{self.image_name}"

        return f"http://i.imgur.com/{self.image_name}"

@public
class DisplayParticlePacket(ClientboundPacket):
    id = (29, 27)

    particle_id:    types.Byte
    x:              types.LimitedLEB128
    y:              types.LimitedLEB128
    velocity_x:     pak.ScaledInteger(types.LimitedLEB128, 100)
    velocity_y:     pak.ScaledInteger(types.LimitedLEB128, 100)
    acceleration_x: pak.ScaledInteger(types.LimitedLEB128, 100)
    acceleration_y: pak.ScaledInteger(types.LimitedLEB128, 100)

@public
class ShowColorPickerPacket(ClientboundPacket):
    id = (29, 32)

    # NOTE: Lua scripting must have been initialized
    # at least once for this to show the interface to
    # the player. When lua scripting gets cleaned up,
    # color pickers are still able to be shown.

    color_picker_id: types.Int
    default_color:   types.Int
    title:           types.String

@public
class LoadInventoryPacket(ClientboundPacket):
    id = (31, 1)

    items: pak.Compound(
        "ItemInfo",

        item_id             = types.Short,
        quantity            = types.UnsignedByte, # NOTE: If item id already received, then this quantity is just added.
        priority            = types.UnsignedByte, # Only used for sorting.
        unk_boolean_4       = types.Boolean,      # Marked as 'is_event' by aiotfm, but I think that's wrong.
        can_use             = types.Boolean,      # Looks like there are some consumables guests aren't allowed to use even if this is 'True'.
        can_equip           = types.Boolean,
        unk_boolean_7       = types.Boolean,
        category            = pak.Enum(types.Byte, enums.ItemCategory),
        can_use_immediately = types.Boolean,
        can_use_when_dead   = types.Boolean,
        image_name          = pak.Optional(types.String, types.Boolean),
        slot                = types.Byte,
    )[types.Short]

@public
class UpdateInventoryPacket(ClientboundPacket):
    id = (31, 2)

    item_id:  types.Short
    quantity: types.UnsignedByte

@public
class UseItemPacket(ClientboundPacket):
    id = (31, 3)

    session_id: types.Int
    item_id:    types.Short

@public
class TradeInvitePacket(ClientboundPacket):
    id = (31, 5)

    session_id: types.Int

@public
class TradeErrorPacket(ClientboundPacket):
    id = (31, 6)

    username: types.String
    error:    pak.Enum(types.Byte, enums.TradeError)

@public
class TradeStartPacket(ClientboundPacket):
    id = (31, 7)

    session_id: types.Int

@public
class UpdateTradeContentsPacket(ClientboundPacket):
    id = (31, 8)

    export:     types.Boolean
    item_id:    types.Short
    increase:   types.Boolean
    quantity:   types.Byte
    image_name: pak.Optional(types.String, types.Boolean)

@public
class TradeLockPacket(ClientboundPacket):
    id = (31, 9)

    trader: pak.Enum(types.Byte, enums.Trader)
    locked: types.Boolean

@public
class TradeCompletePacket(ClientboundPacket):
    id = (31, 10)

@public
class ChangeSatelliteServerPacket(ClientboundPacket):
    """Sent by the main server to tell the client to change the satellite server."""

    id = (44, 1)

    class Ports(pak.Type):
        _default = []

        @classmethod
        def _unpack(cls, buf, *, ctx):
            ports = types.String.unpack(buf, ctx=ctx)

            return [int(port) for port in ports.split("-")]

        @classmethod
        def _pack(cls, value, *, ctx):
            ports = "-".join(str(port) for port in value)

            return types.String.pack(ports, ctx=ctx)

    timestamp: types.Int
    global_id: types.Int
    auth_id:   types.Int

    address: types.String
    ports:   Ports

    @property
    def should_ignore(self):
        return self.address == "x"

@public
class TribulleWrapperPacket(ClientboundPacket):
    id = (60, 3)

    nested: _NestedTribulleType(ClientboundTribullePacket)

@public
class SetTribulleProtocolPacket(ClientboundPacket):
    id = (60, 4)

    new_protocol: types.Boolean

@public
class ShamanObjectPreviewPacket(ClientboundPacket):
    id = (100, 2)

    session_id:       types.Int
    shaman_object_id: types.Short
    x:                types.Short
    y:                types.Short

    # If a rock with children, then the first child's rotation.
    # Else the object's rotation.
    rotation: types.Short

    # Only non-empty if it's a rock.
    # Has format like '2;3,4;5,6' where '2' is the number
    # of children, and then each semicolon-separated pair
    # of numbers is the x,y offset within the parent coordinate
    # system.
    child_offsets: types.String

    is_spawning: types.Boolean

@public
class RemoveShamanObjectPreviewPacket(ClientboundPacket):
    id = (100, 3)

    session_id: types.Int

@public
class VisualConsumableInfoPacket(ClientboundPacket):
    id = (100, 40)

    class _InfoPacket(pak.Packet):
        class Header(pak.Packet.Header):
            id: types.UnsignedByte

    class StartPainting(_InfoPacket):
        id = 1

        paintable_length: pak.ScaledInteger(types.UnsignedShort, 10)
        color:            types.Int

    class PaintLine(_InfoPacket):
        id = 2

        session_id: types.Int
        color:      types.Int
        start_x:    pak.ScaledInteger(types.Int, 10)
        start_y:    pak.ScaledInteger(types.Int, 10)
        end_x:      pak.ScaledInteger(types.Int, 10)
        end_y:      pak.ScaledInteger(types.Int, 10)

    class RemovePaint(_InfoPacket):
        id = 3

        artist_name: types.String

    class ShopCheeseCounter(_InfoPacket):
        id = 4

        session_id:  types.Int
        shop_cheese: types.Int

    class PlaytimeCounter(_InfoPacket):
        id = 5

        session_id: types.Int
        days:       types.UnsignedShort
        hours:      types.Byte

    info: _SimpleNestedPacketType(_InfoPacket)

@public
class LaunchHotAirBalloonPacket(ClientboundPacket):
    id = (100, 71)

    # Sent by the server when someone uses the
    # hot air balloon consumable (item ID 35).

    session_id: types.Int
    badge_id:   types.UnsignedShort

@public
class SetTitlePacket(ClientboundPacket):
    id = (100, 72)

    gender:   pak.Enum(types.UnsignedByte, enums.Gender)
    title_id: types.UnsignedShort

@public
class CollectableActionPacket(ClientboundPacket):
    id = (100, 101)

    class _Action(pak.Packet):
        class Header(pak.Packet.Header):
            id: types.UnsignedByte

    class SetCanCollect(_Action):
        id = 1

        can_collect: types.Boolean

    class AddCarrying(_Action):
        id = 2

        session_id:      types.Int
        image_path:      types.String
        offset_x:        types.Short
        offset_y:        types.Short
        foreground:      types.Boolean
        size_percentage: types.Short
        angle:           types.Short

        @property
        def all_players(self):
            return self.session_id == 0

        @property
        def sprite(self):
            return self.image_path.startswith("$")

    class ClearCarrying(_Action):
        id = 3

        session_id: types.Int

        @property
        def all_players(self):
            return self.session_id == 0

    action: _SimpleNestedPacketType(_Action)

@public
class SetPlayerListPacket(ClientboundPacket):
    id = (144, 1)

    players: types.PlayerDescription[types.Short]

@public
class UpdatePlayerPacket(ClientboundPacket):
    id = (144, 2)

    player:                  types.PlayerDescription
    skip_prepare_animations: types.Boolean
    refresh_player_menu:     types.Boolean

@public
class SetCheesesPacket(ClientboundPacket):
    id = (144, 6)

    session_id: types.Int
    cheeses:    types.Byte

@public
class UnsetShamanPacket(ClientboundPacket):
    id = (144, 7)

    session_id: types.Int

@public
class OpenFashionSquadOutfitsMenuPacket(ClientboundPacket):
    id = (144, 22)

    outfits: pak.Compound(
        "OutfitInfo",

        outfit_id    = types.Int,
        outfit_name  = types.String,
        background   = pak.Enum(types.Byte, enums.FashionSquadOutfitBackground),
        removal_date = types.String,
        outfit_code  = types.String, # TODO: Parse outfit.

        # Might have similar meaning as unk_leb128_6 of sales menu packet.
        unk_byte_6 = types.Byte,
    )[types.Int]

@public
class NPCPlayEmotePacket(ClientboundPacket):
    id = (144, 23)

    name:     types.String
    emote:    pak.Enum(types.Short, enums.Emote)
    emoticon: pak.Enum(types.Short, enums.Emoticon)

@public
class LoadShamanObjectSpritesPacket(ClientboundPacket):
    id = (144, 27)

    shaman_object_id_list: types.LimitedLEB128[types.LimitedLEB128]

    SWF_URL_FMT = "http://www.transformice.com/images/x_bibliotheques/chamanes/o{base_id},{skin_id}.swf"

    @classmethod
    def swf_url(cls, shaman_object_id):
        base_id, skin_id = game.shaman_object_id_parts(shaman_object_id)

        return cls.SWF_URL_FMT.format(base_id=base_id, skin_id=skin_id)

@public
class OpenFashionSquadSalesMenuPacket(ClientboundPacket):
    id = (144, 29)

    sales: pak.Compound(
        "SaleInfo",

        sale_id    = types.LimitedLEB128,
        item_id    = types.String,
        sale_start = types.String,
        sale_end   = types.String,
        percentage = types.LimitedLEB128,

        # Some sort of enum, for colors of sale_start and sale_end.
        #
        # Value '1' cannot cancel the sale, and has color '0xFFD991'.
        # Value '2' can cancel the sale and has color '0xF79337'.
        #
        # Other values are possible and cannot
        # cancel the sale and have color '0x60608F'.
        unk_leb128_6 = types.LimitedLEB128,
    )[types.LimitedLEB128]

@public
class SetCollisionDamagePacket(ClientboundPacket):
    id = (144, 30)

    enabled:     types.ByteBoolean
    sensibility: pak.ScaledInteger(types.LimitedLEB128, 1000)

@public
class SetAdventureBannerPacket(ClientboundPacket):
    id = (144, 31)

    banner_id: types.LimitedLEB128

    IMAGE_URL_FMT = "https://www.transformice.com/images/x_transformice/x_aventure/x_banniere/x_{banner_id}.jpg"

    @property
    def image_url(self):
        return self.IMAGE_URL_FMT.format(banner_id=self.banner_id)

@public
class SetGravityScalePacket(ClientboundPacket):
    id = (144, 32)

    session_id: types.LimitedLEB128

    x: pak.ScaledInteger(types.LimitedLEB128, 1000)
    y: pak.ScaledInteger(types.LimitedLEB128, 1000)

@public
class LoadFurSpritesPacket(ClientboundPacket):
    id = (144, 34)

    fur_id_list: types.LimitedLEB128[types.LimitedLEB128]

    SWF_URL_FMT = "https://www.transformice.com/images/x_bibliotheques/fourrures/f{fur_id}.swf"

    @classmethod
    def swf_url(cls, fur_id):
        """Gets the URL for the SWF containing the textures for the specified fur ID.

        Parameters
        ----------
        fur_id : :class:`int`
            The fur ID to get the URL for.

        Returns
        -------
        :class:`str`
            The URL for the SWF containing the textures.
        """

        return SWF_URL_FMT.format(fur_id=fur_id)

@public
class SetNewsPopupFlyerPacket(ClientboundPacket):
    """Sent by the server to set the image for the popup that shows
    a new event or new limited edition shop items.

    The client is eventually told to load
    ``http://www.transformice.com/images/x_nouveaute/{image_name}``
    and show it on screen.
    """

    id = (144, 35)

    image_name: types.String

    IMAGE_URL_FMT = "https://www.transformice.com/images/x_nouveaute/{image_name}"

    @property
    def image_url(self):
        """The client eventually loads the image at :attr:`IMAGE_URL_FMT`
        and shows it on screen.

        Returns
        -------
        :class:`str`
            The URL for the image.
        """

        return self.IMAGE_URL_FMT.format(image_name=self.image_name)

@public
class SetLanguagePacket(ClientboundPacket):
    id = (176, 5)

    language:               types.String
    country:                types.String
    right_to_left:          types.Boolean
    has_special_characters: types.Boolean
    font:                   types.String

@public
class LanguageSelectionInformationPacket(ClientboundPacket):
    id = (176, 6)

    FLAG_SIZE = 24

    languages: pak.Compound(
        "LanguageInfo",

        code         = types.String,
        display_name = types.String,
        flag_code    = types.String,
    )[types.UnsignedShort]

    def flag_url(self, flag_code):
        return game.flag_url(flag_code, self.FLAG_SIZE)

@public
class ClientVerificationPacket(ClientboundPacket):
    id = (176, 7)

    verification_token: types.Int

@public
class ExtensionWrapperPacket(ClientboundPacket):
    # This ID doesn't seem to be used at all.
    id = (255, 255)

    nested: _NestedExtensionType(ClientboundExtensionPacket)
