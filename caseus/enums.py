import enum

from public import public

@public
class Gender(enum.Enum):
    """A player's gender as described by Transformice."""

    Unknown   = 0
    Feminine  = 1
    Masculine = 2

@public
class LoginMethod(enum.Enum):
    Normal = 0

    # NOTE: There are more values that this could be,
    # but only 'Normal' is used.

# NOTE: The game stores more metadata about communities than we do.
@public
class Community(enum.Enum):
    EN = 0
    FR = 1
    RU = 2
    BR = 3
    ES = 4
    CN = 5
    TR = 6
    VK = 7
    PL = 8
    HU = 9
    NL = 10
    RO = 11
    ID = 12
    DE = 13
    E2 = 14
    AR = 15
    PH = 16
    LT = 17
    JP = 18
    CH = 19
    FI = 20
    CZ = 21
    SK = 22
    HR = 23
    BG = 24
    LV = 25
    HE = 26
    IT = 27
    # NOTE: No 28.
    ET = 29
    AZ = 30
    PT = 31

@public
class ShamanLabel(enum.Enum):
    StayThere      = 0
    FollowMe       = 1
    GoThere        = 2
    WorkInProgress = 3
    KeepCalm       = 4
    GetReady       = 5
    NoIdea         = 6

@public
class Transformation(enum.Enum):
    SmallBox   = 48
    LargeBox   = 49
    Anvil      = 50
    SmallPlank = 51
    LargePlank = 52
    Mouse      = 53

@public
class StaffMessageType(enum.Enum):
    # The 'All' versions send to members of that team in
    # all communities, not just the one the player is in.

    ModeratorRoom       = 0
    AdministratorGlobal = 1
    Arbitre             = 2
    Modo                = 3
    ModoAll             = 4
    AribtreAll          = 5
    ModeratorCommunity  = 6
    LuaTeam             = 7
    MapCrew             = 8
    FunCorp             = 9
    FashionSquad        = 10

@public
class StaffRoleID(enum.Enum):
    NONE = 0

    Arbitre       = 3
    Modo          = 5
    Unknown7      = 7 # Might be sentinel? Never used in game.
    Administrator = 10
    MapCrew       = 11
    LuaTeam       = 12
    FunCorp       = 13
    FashionSquad  = 15

@public
class FashionSquadOutfitBackground(enum.Enum):
    Greenery   = 0
    Beach      = 1
    Ocean      = 2
    Valentines = 3
    Halloween  = 4

    @property
    def url(self):
        return f"https://www.transformice.com/images/x_transformice/x_interface/fonds_shop/{self.value}.jpg"

@public
class IceCubeAction(enum.Enum):
    Unfreeze = 0
    Freeze   = 1

    # NOTE: Not defined in game, just a value which isn't explicitly used.
    SetRemainingTime = 2

    @classmethod
    def _missing_(cls, value):
        return cls.SetRemainingTime

@public
class ItemCategory(enum.Enum):
    Coins           = 10
    Adventure       = 20
    Throwables      = 30
    Arts            = 40
    CostumesAndPets = 50
    Miscellaneous   = 100

@public
class Portal(enum.Enum):
    NONE   = 0
    Blue   = 1
    Orange = 2

    @classmethod
    def _missing_(cls, value):
        # NOTE: Should never happen, but the game
        # would treat unexpected values as 'NONE'.

        return cls.NONE

@public
class ImageTargetType(enum.Enum):
    ReplaceShamanObject = 1
    OverlayPlayer       = 2
    ReplacePlayer       = 3
    BackgroundLayer     = 4
    GroundLayer         = 5
    ForegroundLayer     = 6
    FixedLayerBeforeLua = 7
    FixedLayerBehindLua = 8
    PhysicObject        = 9
    InterfaceLayer      = 10
    OverlayShamanObject = 11

@public
class Emote(enum.Enum):
    NONE = -1

    Dance               = 0
    Laugh               = 1
    Cry                 = 2
    Kiss                = 3
    Mad                 = 4
    Clap                = 5
    Sleep               = 6
    Facepalm            = 7
    Sit                 = 8
    Confetti            = 9
    Flag                = 10
    Marshmallow         = 11
    Selfie              = 12
    Highfive            = 13
    Highfive_1          = 14
    Highfive_2          = 15
    PartyHorn           = 16
    Hug                 = 17
    Hug_1               = 18
    Hug_2               = 19
    Jigglypuff          = 20
    Kissing             = 21
    Kissing_1           = 22
    Kissing_2           = 23
    Feathers            = 24
    RockPaperScissors   = 25
    RockPaperScissors_1 = 26
    RockPaperScissors_2 = 27

    @classmethod
    def _missing_(cls, value):
        return cls.NONE

@public
class Emoticon(enum.Enum):
    NONE = -1

    Smiley    = 0
    Sad       = 1
    Tongue    = 2
    Angry     = 3
    BigSmiley = 4
    Shades    = 5
    Blush     = 6
    Sweatdrop = 7
    Derp      = 8
    OMG       = 9

@public
class VictoryType(enum.Enum):
    Normal    = 0
    Defilante = 1

    # These are used for Mulodrome.
    BlueTeam = 2
    RedTeam  = 3

@public
class NPCInterface(enum.Enum):
    # TODO: Is 'NPCInterface' the best name?

    NONE = 0

    # Executes the 'Clique_Magasin' method
    # on the '$Interface' object. This no
    # longer exists and so will do nothing.
    OldShop = 1

    # Value is specified, however
    # it is never touched in the
    # client code at all.
    Unknown2 = 2

    # Code exists for these but
    # it leads nowhere and can
    # never actually be executed.
    Inert3 = 3
    Inert4 = 4
    Inert5 = 5

    OfficialEvent = 10
    Village       = 11
    Lua           = 12

@public
class NPCItemStatus(enum.Enum):
    CanBuy       = 0
    TooExpensive = 1
    OwnAlready   = 2

@public
class NPCItemType(enum.Enum):
    Badge     = 1
    ShamanOrb = 2
    Title     = 3
    Normal    = 4
    Costume   = 5
