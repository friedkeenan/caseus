r"""Clientbound :class:`~.Packet`\s."""

# TODO: Split this file up. Seriously.

import dataclasses
import typing
import pak

from public import public

from ..common import (
    _NestedLegacyType,
    CompressedSubPacket,
    PlayerInfo,
    RoomProperties,
    ClientboundObjectInfo,
    PlayerFrictionInfo,
    PlayerRotationInfo,
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

    objects: ClientboundObjectInfo[None]

@public
class SetFacingPacket(ClientboundPacket):
    id = (4, 6)

    session_id:   types.Int
    facing_right: types.ByteBoolean

@public
class PlayerActionPacket(ClientboundPacket):
    id = (4, 9)

    session_id: types.Int
    action:     pak.Enum(types.Byte, enums.PlayerAction)
    allow_self: types.ByteBoolean

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
class StartRoundCountdownPacket(ClientboundPacket):
    id = (5, 10)

    activate_countdown: types.Boolean

@public
class AddBonusPacket(ClientboundPacket):
    id = (5, 14)

    x:        types.LEB128
    y:        types.LEB128
    bonus:    pak.Enum(types.LEB128, enums.Bonus)
    angle:    types.LEB128
    bonus_id: types.LEB128
    visible:  types.ByteBoolean

@public
class RemoveObjectPacket(ClientboundPacket):
    id = (5, 15)

    object_id: types.Int

@public
class ExplosionPacket(ClientboundPacket):
    id = (5, 17)

    x: types.LEB128
    y: types.LEB128

    power:  types.LEB128
    radius: types.LEB128

    affect_objects: types.Boolean

@public
class AddShamanObjectPacket(ClientboundPacket):
    id = (5, 20)

    object_id:            types.Int # If '-1' then automatically assigned.
    shaman_object_id:     types.LEB128
    x:                    types.LEB128
    y:                    types.LEB128
    angle:                pak.ScaledInteger(types.LEB128, 100)
    velocity_x:           pak.ScaledInteger(types.LEB128, 100)
    velocity_y:           pak.ScaledInteger(types.LEB128, 100)
    has_contact_listener: types.Boolean
    mice_collidable:      types.ByteBoolean
    colors:               types.Int[types.Byte]

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
class SetObjectGravityScalePacket(ClientboundPacket):
    id = (5, 29)

    object_id: types.Int
    scale:     pak.ScaledInteger(types.Short, 100)

@public
class SetRollingPacket(ClientboundPacket):
    id = (5, 30)

    session_id: types.Int

@public
class SetPlayerSizePacket(ClientboundPacket):
    id = (5, 31)

    session_id:     types.Int
    percentage:     types.UnsignedShort
    exclude_shaman: types.Boolean

@public
class FreezePlayerPacket(ClientboundPacket):
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
class SetPlayerShameowPacket(ClientboundPacket):
    id = (5, 43)

    session_id: types.Int
    enable:     types.Boolean

@public
class EventMapActionPacket(ClientboundPacket):
    id = (5, 44)

    # Only certain actions are available based on
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
class AddCollectiblePacket(ClientboundPacket):
    id = (5, 51)

    adventure_id:   types.UnsignedByte
    individual_id:  types.UnsignedShort # TODO: Better name?
    collectible_id: types.UnsignedByte
    x:              types.Short
    y:              types.Short

@public
class RemoveCollectiblePacket(ClientboundPacket):
    id = (5, 53)

    adventure_id:  types.UnsignedByte
    individual_id: types.UnsignedShort

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

    # If 'True' then 'message' is treated as a translation template.
    should_translate: types.Boolean

    template_args: types.String[types.Byte]

@public
class ServerMessagePacket(ClientboundPacket):
    id = (6, 20)

    general_channel: types.Boolean
    template:        types.String
    template_args:   types.String[types.Byte]

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
            value = types.LEB128.unpack(buf, ctx=ctx)
            if value == cls.IGNORE_VALUE:
                return MovePlayerPacket.IGNORE

            return value

        @classmethod
        def _pack(cls, value, *, ctx):
            if value is MovePlayerPacket.IGNORE:
                value = cls.IGNORE_VALUE

            return types.LEB128.pack(value, ctx=ctx)

    x:                 types.LEB128
    y:                 types.LEB128
    position_relative: types.ByteBoolean
    velocity_x:        _Velocity
    velocity_y:        _Velocity
    velocity_relative: types.ByteBoolean

@public
class ShowEmojiPacket(ClientboundPacket):
    id = (8, 5)

    IMAGE_URL_FMT = "https://www.transformice.com/images/x_transformice/x_smiley/{emoji_id}.png"

    session_id: types.Int
    emoji_id:   types.UnsignedShort

    @property
    def should_remove(self):
        return self.emoji_id == -1

    @property
    def image_url(self):
        return self.IMAGE_URL_FMT.format(emoji_id=self.emoji_id)

@public
class PlayerVictoryPacket(ClientboundPacket):
    id = (8, 6)

    type:       pak.Enum(types.Byte, enums.VictoryType)
    session_id: types.Int
    score:      types.Short
    place:      types.Byte
    seconds:    pak.ScaledInteger(types.UnsignedShort, 100)

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

    class TitleInfo(pak.SubPacket):
        title_id: types.Short
        stars:    types.Byte

    class BadgeInfo(pak.SubPacket):
        badge_id: types.UnsignedShort
        quantity: types.UnsignedShort

    class _Badges(pak.Type):
        _default = []

        @classmethod
        def _unpack(cls, buf, *, ctx):
            length = types.UnsignedShort.unpack(buf, ctx=ctx) // 2

            return [PlayerProfilePacket.BadgeInfo.unpack(buf, ctx=ctx.packet_ctx) for _ in range(length)]

        @classmethod
        def _pack(cls, value, *, ctx):
            length = len(value) * 2

            return (
                types.UnsignedShort.pack(length, ctx=ctx) +

                b"".join(PlayerProfilePacket.BadgeInfo.pack(x, ctx=ctx.packet_ctx) for x in value)
            )

    class GamemodeStatInfo(pak.SubPacket):
        stat_id:           types.UnsignedByte
        quantity:          types.Int
        needed_quantity:   types.Int
        unlocked_badge_id: types.Short

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

    title_id:        types.Short
    unlocked_titles: TitleInfo[types.Short]

    look:   types.String # TODO: Parse outfit.
    level:  types.Short
    badges: _Badges

    gamemode_stats: GamemodeStatInfo[types.Byte]

    cartouche_id:      types.UnsignedByte
    cartouche_id_list: types.UnsignedByte[types.UnsignedByte]

    # NOTE: If the player is not online, then
    # their adventure points will not be displayed.
    #
    # This is because the server only loads a valid
    # value for adventure points if the player is
    # online. This means that you could also think
    # of this field as 'is_online' but that doesn't
    # seem to be the explicit intention.
    display_adventure_points: types.Boolean
    adventure_points:         types.Int

@public
class OldNekodancerProfilePacket(BasePlayerInformationPacket):
    id = (8, 17)

    class StatInfo(pak.SubPacket):
        stat_id:  types.Byte
        quantity: types.Int

    stats: StatInfo[types.Byte]

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
class LoadShopPacket(ClientboundPacket):
    id = (8, 20)

    class OwnedShopItemInfo(pak.SubPacket):
        unique_id: types.LEB128
        favorited: types.Boolean
        colors:    types.LEB128[types.LEB128]

    class ItemInfo(pak.SubPacket):
        category_id: types.UnsignedShort
        item_id:     types.UnsignedShort
        num_colors:  types.Byte
        is_new:      types.Boolean
        info:        pak.Enum(types.Byte, enums.ShopItemInfo)
        cheese_cost: types.Int
        fraise_cost: types.Int
        needed_item: pak.Optional(types.Int, types.Boolean)

    class OutfitInfo(pak.SubPacket):
        outfit_id:  types.UnsignedShort
        look:       types.String # TODO: Parse outfit.
        background: pak.Enum(types.Byte, enums.FashionSquadOutfitBackground)

    @dataclasses.dataclass
    class OwnedShamanObjectInfo:
        shaman_object_id: int
        equipped:         bool
        colors:           typing.Optional[list]

    class _OwnedShamanObjectInfoType(pak.Type):
        @classmethod
        def _unpack(cls, buf, *, ctx):
            shaman_object_id = types.Short.unpack(buf, ctx=ctx)
            equipped         = types.ByteBoolean.unpack(buf, ctx=ctx)
            num_colors       = types.Byte.unpack(buf, ctx=ctx)

            if num_colors == 0:
                colors = None
            else:
                # NOTE: Our use of 'range' will handle non-positive lengths.
                colors = [types.Int.unpack(buf, ctx=ctx) for _ in range(num_colors - 1)]

            return LoadShopPacket.OwnedShamanObjectInfo(shaman_object_id, equipped, colors)

        @classmethod
        def _pack(cls, value, *, ctx):
            if value.colors is None:
                packed_colors_len = types.Byte.pack(0, ctx=ctx)
                packed_colors     = b""
            else:
                packed_colors_len = types.Byte.pack(len(value.colors) + 1, ctx=ctx)
                packed_colors     = b"".join(
                    types.Int.pack(color, ctx=ctx) for color in value.colors
                )

            return (
                types.Short.pack(value.shaman_object_id, ctx=ctx) +
                types.ByteBoolean.pack(value.equipped,   ctx=ctx) +
                packed_colors_len                                 +
                packed_colors
            )

    class ShamanObjectInfo(pak.SubPacket):
        shaman_object_id: types.Int
        num_colors:       types.Byte
        is_new:           types.Boolean
        info:             pak.Enum(types.Byte, enums.ShopItemInfo)
        cheese_cost:      types.Int
        fraise_cost:      types.Short

    class EmojiInfo(pak.SubPacket):
        emoji_id:    types.LEB128
        cheese_cost: types.LEB128
        fraise_cost: types.LEB128
        is_new:      types.Boolean

    cheese:  types.Int
    fraises: types.Int
    look:    types.String # TODO: Parse outfit.

    owned_items: OwnedShopItemInfo[types.LEB128]
    items:       ItemInfo[types.Int]

    outfits:            OutfitInfo[types.Byte]
    owned_outfit_looks: types.String[types.Short] # TODO: Parse outfit.

    owned_shaman_objects: _OwnedShamanObjectInfoType[types.Short]
    shaman_objects:       ShamanObjectInfo[types.Short]

    emojis:          EmojiInfo[types.LEB128]
    owned_emoji_ids: types.LEB128[types.LEB128]

@public
class AddNPCPacket(ClientboundPacket):
    id = (8, 30)

    session_id:       types.Int
    name:             types.String
    title_id:         types.Short
    feminine:         types.Boolean
    look:             types.String # TODO: Parse outfit.
    x:                types.LEB128
    y:                types.LEB128
    emote:            pak.Enum(types.LEB128, enums.Emote)
    facing_right:     types.Boolean
    face_player:      types.Boolean
    interface:        pak.Enum(types.Byte, enums.NPCInterface)
    periodic_message: types.String

@public
class ChangePlayerLookPacket(ClientboundPacket):
    id = (8, 36)

    session_id: types.Int
    look:       types.String

@public
class MeepExplosionPacket(ClientboundPacket):
    id = (8, 38)

    session_id: types.Int
    x:          types.Short
    y:          types.Short
    power:      types.Int

@public
class GiveMeepPacket(ClientboundPacket):
    id = (8, 39)

    can_meep: types.Boolean

@public
class RaiseItemPacket(ClientboundPacket):
    id = (8, 44)

    class _Item(pak.SubPacket):
        class Header(pak.SubPacket.Header):
            id: types.Byte

    class ShopItem(_Item):
        id = 0

        shop_item_id: types.Int

    class ShamanObject(_Item):
        id = 1

        shaman_object_id: types.Int

    class ConsumableReward(_Item):
        id = 2

        reward: pak.Enum(types.Int, enums.ConsumableReward)

    class Badge(_Item):
        id = 3

        badge_id: types.Int

    class InventoryItem(_Item):
        id = 4

        item_id: types.Int

    class Image(_Item):
        id = 5

        image_path: types.String

    class Cartouche(_Item):
        id = 6

        cartouche_id: types.Int

    class Sprite(_Item):
        id = 7

        name:  types.String
        frame: types.UnsignedByte

    class ShopItemCustomization(_Item):
        id = 8

        shop_item_id: types.Int

    class Emoji(_Item):
        id = 9

        emoji_id: types.Int

    session_id: types.Int
    item:       _Item

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
class ShopSpecialOfferPacket(ClientboundPacket):
    id = (20, 3)

    is_sale:             types.Boolean
    is_regular_item:     types.Boolean
    item_id:             types.Int
    enable:              types.Boolean
    ends_timestamp:      types.Int
    discount_percentage: types.Byte

@public
class Unknown_20_4_Packet(ClientboundPacket):
    id = (20, 4)

    class UnknownSubPacket(pak.SubPacket):
        unk_int_1:   types.Int
        unk_int_2:   types.Int
        class_names: types.String[types.Byte]

    unk_array_1: UnknownSubPacket[types.Short]

@public
class ShopCurrencyPacket(ClientboundPacket):
    id = (20, 15)

    cheese:  types.Int
    fraises: types.Int

@public
class LoginSuccessPacket(ClientboundPacket):
    id = (26, 2)

    class CommunityToFlag(pak.Type):
        _default = {}

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
class SetFraisesVisibilityPacket(ClientboundPacket):
    id = (26, 10)

    visible: types.Boolean

@public
class PlayerDamagedPacket(ClientboundPacket):
    id = (26, 11)

    session_id: types.Int

@public
class AccountErrorPacket(ClientboundPacket):
    id = (26, 12)

    # TODO: Enum? Might not be feasible if it
    # has different meanings in different contexts.
    error_code:         types.Byte
    suggested_username: types.String

    unk_string_3: types.String

@public
class CaptchaPacket(ClientboundPacket):
    id = (26, 20)

    class Info(CompressedSubPacket):
        # NOTE: We could make these two fields into a single
        # 'Type' wrapped up together, but there are packets
        # which say they have a custom scale and yet still
        # specify a scale of '1' (this is a real thing that
        # I have observed), and there would be no way to
        # disambiguate such a situation with a 'Type' that
        # only yields the proper scale.
        #
        # Such a situation would have no effect on the client,
        # but I would like to avoid such a situation nonetheless.
        type:  pak.Enum(types.LEB128, enums.CaptchaType)
        scale: pak.Optional(types.LEB128, lambda packet: packet.type is enums.CaptchaType.ScaledColors)

        width:  types.UnsignedShort
        height: types.UnsignedShort

        colors: types.Int[types.UnsignedShort]

    info: Info

    @staticmethod
    def _lerp_white(component, alpha):
        return 0xFF - alpha + ((component * alpha) // 0xFF)

    def draw_image(self):
        from PIL import Image

        im = Image.new("RGB", (self.info.width, self.info.height))
        im.paste(0xFFFFFF, (0, 0, self.info.width, self.info.height))

        for i, color in enumerate(self.info.colors):
            y, x = divmod(i, self.info.width)

            if self.info.scale is not None:
                color *= self.info.scale

            color &= 0xFFFFFFFF

            alpha = (color >> 24) & 0xFF
            red   = (color >> 16) & 0xFF
            green = (color >>  8) & 0xFF
            blue  = (color >>  0) & 0xFF

            rgb = tuple(self._lerp_white(component, alpha) for component in (red, green, blue))

            im.putpixel((x, y), rgb)

        return im

@public
class IPSPongPacket(ClientboundPacket):
    id = (26, 25)

@public
class AddOfficialImagesPacket(ClientboundPacket):
    id = (26, 31)

    class ImageInfo(pak.SubPacket):
        class TileInfo(pak.SubPacket):
            # Unused. Maybe some sort of ID?
            unk_short_1: types.Short

            x_step: pak.ScaledInteger(types.Int, 100)
            y_step: pak.ScaledInteger(types.Int, 100)

        image_path: types.String

        # If true calls an empty function which is named the same
        # as other functions which look like "center" or "align".
        unk_boolean_2: types.Boolean

        x: types.Short
        y: types.Short

        # Only used when tiled.
        width:  types.Short
        height: types.Short

        target: pak.Enum(types.Byte, enums.OfficialImageTarget)

        tile_info: pak.Optional(TileInfo, types.Boolean)

        disappear_on_click: types.Boolean
        hidden:             types.Boolean

        # Only for use with 'RemoveOfficialImagePacket'.
        name: types.String

    images: ImageInfo[types.UnsignedByte]

@public
class RoomListPacket(ClientboundPacket):
    id = (26, 35)

    class RoomInfo(pak.SubPacket):
        class Header(pak.SubPacket.Header):
            id: types.Byte

        community: types.String
        flag_code: types.String
        name:      types.String

    class NormalRoomInfo(RoomInfo):
        id = 0

        num_players: types.UnsignedShort
        max_players: types.UnsignedByte
        is_funcorp:  types.Boolean
        properties:  pak.Optional(RoomProperties, types.Boolean)

    # NOTE: Called 'pinned' rooms by other libraries.
    # These rooms are indeed sorted above all other
    # room entries, but I don't think that's the only
    # purpose of these entries.
    class SpecialRoomInfo(RoomInfo):
        id = 1

        num_players_description: types.String
        type:                    types.String
        argument:                types.String

        @property
        def num_players(self):
            separator_index = self.num_players_description.find("/")

            if separator_index > 0:
                num_players = self.num_players_description[:separator_index]
            else:
                num_players = self.num_players_description

            if len(num_players) <= 0:
                return 0

            return int(num_players)

        @property
        def children_info(self):
            # "lm" is likely short for "Lua Module".
            if self.type != "lm":
                return None

            children = []
            for description in self.argument.split("&~"):
                name, num_players = description.split(",")

                children.append(dict(name=name, num_players=int(num_players)))

            return children

    game_modes:         pak.Enum(types.Byte, enums.GameMode)[types.Byte]
    selected_game_mode: pak.Enum(types.Byte, enums.GameMode)
    rooms:              RoomInfo[None]

@public
class OpenNPCShopPacket(ClientboundPacket):
    id = (26, 38)

    class ItemInfo(pak.SubPacket):
        status: pak.Enum(types.UnsignedByte, enums.NPCItemStatus)

        type:     pak.Enum(types.UnsignedByte, enums.NPCItemType)
        item_id:  types.Int
        quantity: types.Short

        # Cost type is always 'NPCItemType.Inventory' because you
        # always spend inventory items to buy items from an NPC.
        cost_type:     pak.Enum(types.UnsignedByte, enums.NPCItemType)
        cost_id:       types.Int
        cost_quantity: types.Short

        hover_text_template: types.String
        hover_text_args:     types.String

    name:  types.String
    items: ItemInfo[types.UnsignedByte]

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
class ShopBaseTimestampPacket(ClientboundPacket):
    id = (28, 2)

    timestamp: types.Int

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

    template:      types.String
    template_args: types.String[types.Byte]

@public
class PingPacket(ClientboundPacket):
    id = (28, 6)

    payload:     types.Byte
    main_server: types.Boolean

@public
class ClientInformationPacket(ClientboundPacket):
    id = (28, 50)

    http_info_url: types.ShiftedString

@public
class SetAllowEmailAddressPacket(ClientboundPacket):
    id = (28, 62)

    allow_email: types.Boolean

@public
class ChangeMainServerPacket(ClientboundPacket):
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
            return "http://images.atelier801.com/ArmorGame.png"

        if self.image_name.startswith("img@"):
            return f"http://avatars.atelier801.com/module/{self.image_name.remove_prefix('img@')}.png"

        if self.image_name.startswith("discord@"):
            return f"http://media.discordapp.net/attachments/{self.image_name.remove_prefix('discord@')}"

        if len(self.image_name) > 12:
            return f"http://images.atelier801.com/{self.image_name}"

        return f"http://i.imgur.com/{self.image_name}"

@public
class DisplayParticlePacket(ClientboundPacket):
    id = (29, 27)

    particle_id:    types.Byte
    x:              types.LEB128
    y:              types.LEB128
    velocity_x:     pak.ScaledInteger(types.LEB128, 100)
    velocity_y:     pak.ScaledInteger(types.LEB128, 100)
    acceleration_x: pak.ScaledInteger(types.LEB128, 100)
    acceleration_y: pak.ScaledInteger(types.LEB128, 100)

@public
class AddPhysicObjectPacket(ClientboundPacket):
    id = (29, 28)

    physic_id:            types.LEB128
    dynamic:              types.Boolean
    ground_id:            types.Byte
    x:                    types.LEB128
    y:                    types.LEB128
    width:                types.LEB128
    height:               types.LEB128
    foreground:           types.Boolean
    friction:             pak.ScaledInteger(types.LEB128, 100)
    restitution:          pak.ScaledInteger(types.LEB128, 100)
    angle:                types.LEB128
    has_color:            types.Boolean
    color:                types.Int
    mice_collidable:      types.Boolean
    ground_collidable:    types.Boolean
    fixed_rotation:       types.Boolean
    mass:                 types.LEB128
    linear_damping:       pak.ScaledInteger(types.LEB128, 100)
    angular_damping:      pak.ScaledInteger(types.LEB128, 100)
    invisible:            types.Boolean
    image_description:    types.String
    has_contact_listener: types.Boolean

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

    class ItemInfo(pak.SubPacket):
        item_id: types.Short

        # NOTE: If item id already received, then this quantity is just added.
        quantity: types.UnsignedShort

        # Only used for sorting.
        sorting_id: types.UnsignedShort
        priority:   types.UnsignedByte
        is_event:   types.Boolean

        # Looks like there are some consumables guests aren't allowed to use even if this is 'True'.
        can_use: types.Boolean

        can_equip: types.Boolean
        can_trade: types.Boolean

        category: pak.Enum(types.Byte, enums.ItemCategory)

        # If the 'initial_cooldown' field is non-zero, and if
        # the client has not received a 'DisableInitialItemCooldownPacket'
        # since the round started, then the following logic is applied:
        #
        # If the current map category is 'Racing', 'RacingTest',
        # or 'NoShamanTest', then this value is hardcoded to '30'.
        # Additionally if playing those categories, then items
        # cannot be used before a player has won the round.
        #
        # Else, if the map has a shaman but the shaman is dead,
        # then there is no time constraint on when items can be
        # used, overriding this field.
        #
        # After the above logic, then if the item has ID '2578',
        # corresponding to the trampoline item, then if the map
        # has no shaman, or strangely if the map has a shaman but
        # the shaman is dead, then the item cannot be used. The
        # latter case seems maybe unintentional since the game
        # still sets the cooldown to '0' before returning from
        # the function, and does not send any message that the
        # item can't be used. However if it is unintentional,
        # then there would be no reason for that condition to
        # exist because it was already covered by earlier behavior.
        #
        # Else this field names the seconds after a round has
        # begun after which the item can be used.
        initial_cooldown: types.Byte

        can_use_when_dead: types.Boolean
        image_name:        pak.Optional(types.String, types.Boolean)
        slot:              types.Byte

    items: ItemInfo[types.Short]

@public
class UpdateInventoryPacket(ClientboundPacket):
    id = (31, 2)

    item_id:  types.Short
    quantity: types.UnsignedShort

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

    for_self:   types.Boolean
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

    nested: ClientboundTribullePacket

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

    # If a rock with children, then the first child's angle.
    # Else the object's angle.
    angle: types.Short

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
class SetRockPaperScissorsChoicesPacket(ClientboundPacket):
    id = (100, 5)

    first_session_id:  types.Int
    first_choice:      pak.Enum(types.Byte, enums.RockPaperScissorsChoice)
    second_session_id: types.Int
    second_choice:     pak.Enum(types.Byte, enums.RockPaperScissorsChoice)

@public
class RemoveOfficialImagePacket(ClientboundPacket):
    id = (100, 10)

    name: types.String

@public
class VisualConsumableInfoPacket(ClientboundPacket):
    id = (100, 40)

    class _InfoPacket(pak.SubPacket):
        class Header(pak.SubPacket.Header):
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

    info: _InfoPacket

@public
class ImmobilizePlayerPacket(ClientboundPacket):
    id = (100, 66)

    immobilize: types.Boolean

@public
class NotificationPacket(ClientboundPacket):
    # NOTE: I am not happy with the name of
    # this packet, but I don't know what other
    # purpose it could have considering they
    # planned ahead to have different IDs do
    # different things.

    id = (100, 67)

    class Notification(pak.SubPacket):
        class Header(pak.SubPacket.Header):
            id: types.Byte

    class GainItemNotification(Notification):
        id = 0

        item_id:  types.UnsignedShort
        quantity: types.UnsignedShort

    notification: Notification

@public
class AttachSpritePacket(ClientboundPacket):
    id = (100, 69)

    session_id: types.Int
    sprite:     types.String
    offset_x:   types.Short
    offset_y:   types.Short

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
class ChangeLoginBackgroundPacket(ClientboundPacket):
    id = (100, 99)

    @dataclasses.dataclass
    class BackgroundInfo:
        IMAGE_URL_FMT = "https://www.transformice.com/images/x_transformice/x_connexion/{image}"

        background_image: str
        foreground_image: str

        mouse_offset_x: int
        mouse_offset_y: int

        @property
        def background_image_url(self):
            return self.IMAGE_URL_FMT.format(image=self.background_image)

        @property
        def foreground_image_url(self):
            if len(self.foreground_image) <= 0:
                return None

            return self.IMAGE_URL_FMT.format(image=self.foreground_image)

    class _BackgroundInfo(pak.Type):
        @classmethod
        def _unpack(cls, buf, *, ctx):
            description = types.String.unpack(buf, ctx=ctx)

            background_image, *rest = description.split("#")

            return ChangeLoginBackgroundPacket.BackgroundInfo(
                background_image = background_image,
                foreground_image = rest[0] if len(rest) > 0 else "",

                mouse_offset_x = int(rest[1]) if len(rest) > 1 else 0,
                mouse_offset_y = int(rest[2]) if len(rest) > 2 else 0,
            )

        @classmethod
        def _pack(cls, value, *, ctx):
            description = value.background_image

            if len(value.foreground_image) > 0:
                description += f"#{value.foreground_image}"
            elif value.mouse_offset_x != 0 or value.mouse_offset_y != 0:
                description += "#"

            if value.mouse_offset_x != 0:
                description += f"#{value.mouse_offset_x}"
            else:
                description += "#"

            if value.mouse_offset_y != 0:
                description += f"#{value.mouse_offset_y}"

            return types.String.pack(description, ctx=ctx)

    background: _BackgroundInfo

@public
class CollectibleActionPacket(ClientboundPacket):
    id = (100, 101)

    class _Action(pak.SubPacket):
        class Header(pak.SubPacket.Header):
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

    action: _Action

@public
class SetPlayerListPacket(ClientboundPacket):
    id = (144, 1)

    players: PlayerInfo[types.Short]

@public
class UpdatePlayerListPacket(ClientboundPacket):
    id = (144, 2)

    player:                  PlayerInfo
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
class PlayShamanInvocationSoundPacket(ClientboundPacket):
    id = (144, 9)

    shaman_object_id: types.Byte

    @property
    def use_nail_sound(self):
        return self.shaman_object_id == -1

@public
class PlaySoundPacket(ClientboundPacket):
    id = (144, 10)

    SOUND_URL_FMT = "http://audio.atelier801.com/transformice/{sound}.mp3"

    class LocationInfo(pak.SubPacket):
        x: types.Short
        y: types.Short

    sound:    types.String
    volume:   pak.ScaledInteger(types.Short, 100)
    location: pak.Optional(LocationInfo, types.Boolean)

    @property
    def sound_url(self):
        return self.SOUND_URL_FMT.format(sound=self.sound)

@public
class RoomPropertiesPacket(ClientboundPacket):
    id = (144, 18)

    properties: RoomProperties

@public
class OpenFashionSquadOutfitsMenuPacket(ClientboundPacket):
    id = (144, 22)

    class OutfitInfo(pak.SubPacket):
        outfit_id:    types.Int
        outfit_name:  types.String
        background:   pak.Enum(types.Byte, enums.FashionSquadOutfitBackground)
        removal_date: types.String
        look:         types.String # TODO: Parse outfit.

        # Might have similar meaning as unk_leb128_6 of sales menu packet.
        unk_byte_6: types.Byte

    outfits: OutfitInfo[types.Int]

@public
class NPCPlayEmotePacket(ClientboundPacket):
    id = (144, 23)

    name:     types.String
    emote:    pak.Enum(types.Short, enums.Emote)
    emoji_id: types.Short

@public
class DecoratePlayerListPacket(ClientboundPacket):
    id = (144, 26)

    class Decoration(pak.SubPacket):
        class Header(pak.SubPacket.Header):
            id: types.LEB128

    class VersusEventCounter(Decoration):
        id = 1

        class TeamInfo(pak.SubPacket):
            image_name:      types.String
            gathered_cheese: types.String
            text_color:      types.LEB128

        left:  TeamInfo
        right: TeamInfo

    decoration: Decoration

@public
class LoadShamanObjectSpritesPacket(ClientboundPacket):
    id = (144, 27)

    shaman_object_id_list: types.LEB128[types.LEB128]

    SWF_URL_FMT = "http://www.transformice.com/images/x_bibliotheques/chamanes/o{base_id},{skin_id}.swf"

    @classmethod
    def swf_url(cls, shaman_object_id):
        base_id, skin_id = game.shaman_object_id_parts(shaman_object_id)

        return cls.SWF_URL_FMT.format(base_id=base_id, skin_id=skin_id)

@public
class OpenFashionSquadSalesMenuPacket(ClientboundPacket):
    id = (144, 29)

    class SaleInfo(pak.SubPacket):
        sale_id:    types.LEB128
        item_id:    types.String
        sale_start: types.String
        sale_end:   types.String
        percentage: types.LEB128

        # Some sort of enum, for colors of sale_start and sale_end.
        #
        # Value '1' cannot cancel the sale, and has color '0xFFD991'.
        # Value '2' can cancel the sale and has color '0xF79337'.
        #
        # Other values are possible and cannot
        # cancel the sale and have color '0x60608F'.
        unk_leb128_6: types.LEB128

    sales: SaleInfo[types.LEB128]

@public
class SetCollisionDamagePacket(ClientboundPacket):
    id = (144, 30)

    enabled:     types.ByteBoolean
    sensibility: pak.ScaledInteger(types.LEB128, 1000)

@public
class SetAdventureBannerPacket(ClientboundPacket):
    id = (144, 31)

    banner_id: types.LEB128

    IMAGE_URL_FMT = "https://www.transformice.com/images/x_transformice/x_aventure/x_banniere/x_{banner_id}.jpg"

    @property
    def image_url(self):
        return self.IMAGE_URL_FMT.format(banner_id=self.banner_id)

@public
class SetGravityScalePacket(ClientboundPacket):
    id = (144, 32)

    session_id: types.LEB128

    x: pak.ScaledInteger(types.LEB128, 1000)
    y: pak.ScaledInteger(types.LEB128, 1000)

@public
class LoadFurSpritesPacket(ClientboundPacket):
    id = (144, 34)

    fur_id_list: types.LEB128[types.LEB128]

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
class DisplayDismissibleImagePacket(ClientboundPacket):
    id = (144, 37)

    IMAGE_URL_FMT = "http://www.transformice.com/images/{image_path}"

    image_path: types.String

    @property
    def image_url(self):
        if "://" in self.image_path:
            return self.image_path

        return self.IMAGE_URL_FMT.format(image_path=self.image_path)

@public
class SetCheeseSpriteSuffxPacket(ClientboundPacket):
    id = (144, 39)

    suffix: types.String

@public
class SetPlayerCollisionPacket(ClientboundPacket):
    id = (144, 43)

    class CollisionFlags(pak.BitField):
        standard_player:              1
        colliding_player:             1
        standard_object:              1
        non_player_colliding_object:  1
        only_player_colliding_object: 1
        non_colliding:                1

        # Theoretically these extraneous
        # bits could be set to impact
        # collisions between players,
        # but that would be weird.
        _custom_bits: 26

    session_id: types.LEB128

    collision_preset: pak.Enum(types.LEB128, enums.CollisionPreset)

    # Only used if 'Manual' is used as 'collision_preset'.
    personal_categories:      CollisionFlags.Type(types.LEB128)
    collides_with_categories: CollisionFlags.Type(types.LEB128)

@public
class AvailableEmojisPacket(ClientboundPacket):
    id = (144, 44)

    DEFAULT_EMOJI_IDS = range(1, 10 + 1)

    # Emojis besides the default ones.
    extra_emoji_ids: types.LEB128[types.LEB128]

    @property
    def available_emoji_ids(self):
        return [*self.DEFAULT_EMOJI_IDS, *self.extra_emoji_ids]

@public
class DisableSynchronizationPacket(ClientboundPacket):
    id = (144, 45)

@public
class DisableInitialItemCooldownPacket(ClientboundPacket):
    id = (144, 46)

@public
class SaveWallpaperPacket(ClientboundPacket):
    id = (144, 47)

    # NOTE: The game downloads the image as a JPEG but
    # then before saving it, converts the image to a PNG.
    IMAGE_URL_FMT = "https://www.transformice.com/images/wallpaper/{name}.jpg"

    wallpaper_name: types.String

    @property
    def image_url(self):
        return self.IMAGE_URL_FMT.format(name=self.wallpaper_name)

@public
class PlayerMovementPacket(ClientboundPacket):
    id = (144, 48)

    session_id:          types.LEB128
    moving_right:        types.Boolean
    moving_left:         types.Boolean
    x:                   pak.ScaledInteger(types.LEB128, 100 / 30)
    y:                   pak.ScaledInteger(types.LEB128, 100 / 30)
    velocity_x:          pak.ScaledInteger(types.LEB128, 10)
    velocity_y:          pak.ScaledInteger(types.LEB128, 10)
    friction_info:       PlayerFrictionInfo
    jumping:             types.Boolean
    jumping_frame_index: types.LEB128
    entered_portal:      pak.Enum(types.LEB128, enums.Portal)

    # Only present if transformed or rolling.
    rotation_info: pak.Optional(PlayerRotationInfo)

@public
class ChangeNPCLookPacket(ClientboundPacket):
    id = (144, 49)

    name: types.String
    look: types.String # TODO: Parse outfit.

@public
class RemoveNPCPacket(ClientboundPacket):
    id = (144, 50)

    name: types.String

@public
class SetLanguagePacket(ClientboundPacket):
    id = (176, 5)

    language:               types.String
    country:                types.String
    right_to_left:          types.Boolean
    has_special_characters: types.Boolean
    font:                   types.String

@public
class AvailableLanguagesPacket(ClientboundPacket):
    id = (176, 6)

    FLAG_SIZE = 24

    class LanguageInfo(pak.SubPacket):
        code:         types.String
        display_name: types.String
        flag_code:    types.String

    languages: LanguageInfo[types.UnsignedShort]

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

    nested: ClientboundExtensionPacket
