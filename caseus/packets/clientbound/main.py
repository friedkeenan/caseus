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

from ...game import Room, flag_url

@public
class LegacyWrapperPacket(ClientboundPacket):
    id = (1, 1)

    nested: _NestedLegacyType(ClientboundLegacyPacket)

@public
class Unknown_4_2_Packet(ClientboundPacket):
    id = (4, 2)

    unk_byte_1:    types.Byte
    unk_short_2:   types.Short
    unk_short_3:   types.Short
    unk_byte_4:    types.Byte
    unk_boolean_5: types.Boolean
    unk_short_6:   types.Short

@public
class Unknown_4_3_Packet(ClientboundPacket):
    id = (4, 3)

    class UnknownType(pak.Type):
        @dataclasses.dataclass
        class Value:
            attr_1:  int
            attr_2:  int
            attr_3:  bool
            attr_4:  float
            attr_5:  float
            attr_6:  float
            attr_7:  float
            attr_8:  float
            attr_9:  float
            attr_10: bool
            attr_11: bool
            attr_12: bool

            def __init__(
                self,

                param_1,
                param_2,
                param_3 = 0,
                param_4 = 0,
                param_5 = 0,
                param_6 = 0,
                param_7 = 0,
                param_8 = 0,
                param_9 = False,
                param_10 = False,
                param_11 = False,
            ):
                self.attr_1 = param_1
                self.attr_2 = param_2
                self.attr_3 = (param_2 == -1)

                self.attr_4 = param_3 / 100
                self.attr_5 = param_4 / 100
                self.attr_6 = param_5 / 100
                self.attr_7 = param_6 / 100
                self.attr_8 = param_7 / 100
                self.attr_9 = param_8 / 100

                self.attr_10 = param_9
                self.attr_11 = param_10
                self.attr_12 = param_11

        @classmethod
        def _unpack(cls, buf, *, ctx):
            unk_1 = types.Int.unpack(buf, ctx=ctx)
            unk_2 = types.Short.unpack(buf, ctx=ctx)

            if unk_2 == -1:
                return cls.Value(unk_1, -1)

            return cls.Value(
                unk_1,
                unk_2,

                types.Int.unpack(buf, ctx=ctx),
                types.Int.unpack(buf, ctx=ctx),

                types.Short.unpack(buf, ctx=ctx),
                types.Short.unpack(buf, ctx=ctx),
                types.Short.unpack(buf, ctx=ctx),
                types.Short.unpack(buf, ctx=ctx),

                types.Boolean.unpack(buf, ctx=ctx),
                types.Boolean.unpack(buf, ctx=ctx),

                types.Byte.unpack(buf, ctx=ctx) == 1
            )

        @classmethod
        def _pack(cls, value, *, ctx):
            data = (
                types.Int.pack(value.attr_1, ctx=ctx) +
                types.Short.pack(value.attr_2, ctx=ctx)
            )

            if value.attr_2 == -1:
                return data

            return data + (
                types.Int.pack(int(value.attr_4 * 100)) +
                types.Int.pack(int(value.attr_5 * 100)) +
                types.Int.pack(int(value.attr_6 * 100)) +
                types.Int.pack(int(value.attr_7 * 100)) +
                types.Int.pack(int(value.attr_8 * 100)) +
                types.Int.pack(int(value.attr_9 * 100)) +

                types.Boolean.pack(value.attr_10) +
                types.Boolean.pack(value.attr_11) +

                types.Byte.pack(1 if value.attr_11 else 0)
            )

    values: UnknownType[None]

@public
class NewMapPacket(ClientboundPacket):
    id = (5, 2)

    code: types.Int

    unk_short_2: types.Short
    unk_byte_3: types.Byte

    xml: types.CompressedString

    author: types.String
    perm_code: types.Byte
    mirrored: types.Boolean

    unk_boolean_8: types.Boolean
    unk_boolean_9: types.Boolean
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
class JoinedRoomPacket(ClientboundPacket):
    id = (5, 21)

    official:  types.Boolean
    raw_name:  types.String
    flag_code: types.String

    def room(self):
        return Room(
            official  = self.official,
            raw_name  = self.raw_name,
            flag_code = self.flag_code,
        )

@public
class SetMapTimerPacket(ClientboundPacket):
    id = (5, 22)

    seconds: types.Short

@public
class RoomMessagePacket(ClientboundPacket):
    id = (6, 6)

    username: types.String
    message:  types.String

    # Seems to always be 'False', and the value
    # doesn't seem to matter in the game code.
    unk_boolean_3: types.Boolean

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

    # This seems like it could be staff role IDs the user has?
    unk_array_7: types.Byte[types.Byte]

    # Seems like you can repeat the same message if this is true.
    # Also seems connected to staff roles. Maybe it's true if you
    # have a moderator-ish role?
    unk_bool_8: types.Boolean

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
class SetCanTransform(ClientboundPacket):
    id = (27, 10)

    can_transform: types.Boolean

@public
class SetTransformation(ClientboundPacket):
    id = (27, 11)

    session_id:     types.Int
    transformation: pak.Enum(types.Short, enums.Transformation)

@public
class ReaffirmServerAddressPacket(ClientboundPacket):
    """Sent to the client to make sure it's connected to the expected server."""

    id = (28, 98)

    address: types.String

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
class SetLoginBannerPacket(ClientboundPacket):
    id = (144, 31)

    week_number: pak.LEB128

    IMAGE_URL_FMT = "https://www.transformice.com/images/x_transformice/x_aventure/x_banniere/x_{week_number}.jpg"

    @property
    def image_url(self):
        # TODO: Docs.

        return self.IMAGE_URL_FMT.format(week_number=self.week_number)

@public
class QueueLoadFurTextures(ClientboundPacket):
    id = (144, 34)

    fur_id_list: pak.LEB128[pak.LEB128]

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
        return flag_url(flag_code, self.FLAG_SIZE)

@public
class ExtensionWrapperPacket(ClientboundPacket):
    # This ID doesn't seem to be used at all.
    id = (255, 255)

    nested: _NestedExtensionType(ClientboundExtensionPacket)
