r"""Clientbound :class:`~.Packet`\s."""

import dataclasses
import pak

from public import public

from ..common import (
    _NestedLegacyType,
    _NestedTribulleType,
    _NestedExtensionType,
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
class PlayerMovementPacket(ClientboundPacket):
    id = (4, 4)

    session_id:          types.Int
    room_map_id:         types.Int
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
class NewMapPacket(ClientboundPacket):
    id = (5, 2)

    code: types.Int

    unk_short_2: types.Short

    room_map_id: types.Byte
    xml:         types.CompressedString
    author:      types.String
    perm_code:   types.Byte
    mirrored:    types.Boolean

    unk_boolean_8:  types.Boolean
    unk_boolean_9:  types.Boolean
    unk_boolean_10: types.Boolean

    unk_int_11: types.Int

@public
class CreateShamanLabel(ClientboundPacket):
    """Sent by the satellite server to create a shaman label."""

    id = (5, 9)

    label: pak.Enum(types.Byte, enums.ShamanLabel)
    x:     types.Short
    y:     types.Short

@public
class AddShamanObjectPacket(ClientboundPacket):
    id = (5, 20)

    object_id:        types.Int # If '-1' then automatically assigned.
    shaman_object_id: types.Short
    x:                types.Short
    y:                types.Short
    angle:            types.Short
    velocity_x:       types.Byte
    velocity_y:       types.Byte
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
class SetMapTimerPacket(ClientboundPacket):
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

    # Ignored if '0'.
    milliseconds_to_send_previous: types.Int

    x: types.Int
    y: types.Int

@public
class FreezePacket(ClientboundPacket):
    id = (5, 34)

    session_id: types.Int
    freeze:     types.Boolean
    show_ice:   types.Boolean

@public
class SpawnParticlePacket(ClientboundPacket):
    id = (5, 50)

    particle_id: types.Byte # TODO: Enum?
    x:           types.Short
    y:           types.Short

@public
class RoomMessagePacket(ClientboundPacket):
    id = (6, 6)

    username: types.String
    message:  types.String

    # Seems to always be 'False', and the value
    # doesn't seem to matter in the game code.
    unk_boolean_3: types.Boolean

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
    # 'ModeratorCommunity' messages types, then nothing is displayed.
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
class MakeShamanPacket(ClientboundPacket):
    id = (8, 12)

    session_id:    types.Int
    unk_byte_2:    types.Byte
    unk_short_3:   types.Short
    unk_ushort_4:  types.UnsignedShort
    unk_boolean_5: types.Boolean
    unk_int_6:     types.Int

@public
class MovePlayerPacket(ClientboundPacket):
    id = (8, 3)

    x:                 types.Short
    y:                 types.Short
    position_relative: types.ByteBoolean
    velocity_x:        types.Short
    velocity_y:        types.Short
    velocity_relative: types.ByteBoolean

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

    # I'm at least *pretty* sure
    # that this corresponds to
    # transmissiblity. It is
    # stored globally and not
    # per-player however.
    transmissible: types.Boolean

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

    staff_role_ids: pak.Enum(types.Byte, enums.StaffRoleID)[types.Byte]

    # Seems like you can repeat the same message if this is true.
    # Also seems connected to staff roles. Maybe it's true if you
    # have a moderator-ish role?
    unk_boolean_8: types.Boolean

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
class PongPacket(ClientboundPacket):
    id = (26, 25)

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
class ReaffirmServerAddressPacket(ClientboundPacket):
    """Sent to the client to make sure it's connected to the expected server."""

    id = (28, 98)

    address: types.String

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
class LoadInventoryPacket(ClientboundPacket):
    id = (31, 1)

    consumables: pak.Compound(
        "ConsumableInfo",

        consumable_id       = types.Short,
        quantity            = types.UnsignedByte, # NOTE: If consumable id already received, then this quantity is just added.
        priority            = types.UnsignedByte, # Only used for sorting.
        is_event            = types.Boolean,      # Is this correct?
        can_use             = types.Boolean,      # Looks like there are some consumables guests aren't allowed to use even if this is 'True'.
        can_equip           = types.Boolean,
        unk_boolean_7       = types.Boolean,
        category            = pak.Enum(types.Byte, enums.ConsumableCategory),
        can_use_immediately = types.Boolean,
        can_use_when_dead   = types.Boolean,
        image_name          = pak.Optional(types.String, types.Boolean),
        slot                = types.Byte,
    )[types.Short]

@public
class UpdateInventoryPacket(ClientboundPacket):
    id = (31, 2)

    consumable_id: types.Short
    quantity:      types.UnsignedByte

@public
class UseConsumablePacket(ClientboundPacket):
    id = (31, 3)

    session_id:    types.Int
    consumable_id: types.Short

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
class SetHandlingTribullePackets(ClientboundPacket):
    id = (60, 4)

    handle_tribulle_packets: types.Boolean

@public
class SetTitlePacket(ClientboundPacket):
    id = (100, 72)

    gender:   pak.Enum(types.UnsignedByte, enums.Gender)
    title_id: types.UnsignedShort

@public
class SetActivePlayersPacket(ClientboundPacket):
    id = (144, 1)

    players: types.PlayerDescription[types.Short]

@public
class UpdateActivePlayerPacket(ClientboundPacket):
    id = (144, 2)

    player: types.PlayerDescription

    unk_boolean_2: types.Boolean

    # If 'True', then it resets a timer which calls an empty function every second.
    unk_boolean_3: types.Boolean

@public
class SetCheesesPacket(ClientboundPacket):
    id = (144, 6)

    session_id: types.Int
    cheeses:    types.Byte

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
    )[types.VarInt]

@public
class SetLoginBannerPacket(ClientboundPacket):
    id = (144, 31)

    week_number: types.LimitedLEB128

    IMAGE_URL_FMT = "https://www.transformice.com/images/x_transformice/x_aventure/x_banniere/x_{week_number}.jpg"

    @property
    def image_url(self):
        # TODO: Docs.

        return self.IMAGE_URL_FMT.format(week_number=self.week_number)

@public
class SetGravityScalePacket(ClientboundPacket):
    id = (144, 32)

    session_id: types.LimitedLEB128

    x: types.LimitedLEB128
    y: types.LimitedLEB128

@public
class QueueLoadFurTexturesPacket(ClientboundPacket):
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
class ExtensionWrapperPacket(ClientboundPacket):
    # This ID doesn't seem to be used at all.
    id = (255, 255)

    nested: _NestedExtensionType(ClientboundExtensionPacket)
