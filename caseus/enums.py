import enum

from public import public

@public
class RefereeID(enum.Enum):
    # The non-zero values seem to have
    # been taken from creating an account
    # and then deleting the account, freeing
    # up the ID for these specific referees.

    Unknown  = 0
    Facebook = 58524153
    Steam    = 65102833

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
class TribulleCommunity(enum.Enum):
    EN = 1
    FR = 2
    RU = 3
    BR = 4
    ES = 5
    CN = 6
    TR = 7
    VK = 8
    PL = 9
    HU = 10
    NL = 11
    RO = 12
    ID = 13
    DE = 14
    E2 = 15
    AR = 16
    PH = 17
    LT = 18
    JP = 19
    CH = 20
    FI = 21
    CZ = 22
    HR = 23
    SK = 24
    BG = 25
    LV = 26
    HE = 27
    IT = 28
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
class StaffRole(enum.Enum):
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
    Cartouche = 2
    Title     = 3
    Normal    = 4
    Costume   = 5

@public
class MapCategory(enum.Enum):
    # NOTE: There are certain categories
    # which are listed on the wiki but we
    # do not list here. This is because the
    # game does not know about them or treat
    # them specially at all.

    Standard               = 0
    Protected              = 1
    Prime                  = 2
    PrimeBootcamp          = 3
    Shaman                 = 4
    Art                    = 5
    Mechanism              = 6
    NoShaman               = 7
    DualShaman             = 8
    Miscellaneous          = 9
    Survivor               = 10
    VampireSurvivor        = 11
    Bootcamp               = 13
    Racing                 = 17
    Defilante              = 18
    Music                  = 19
    SurvivorTest           = 20
    VampireSurvivorTest    = 21
    TribeHouse             = 22
    BootcampTest           = 23
    DualShamanSurvivor     = 24
    DualShamanTest         = 32
    DualShamanSurvivorTest = 34
    Module                 = 41
    NoShamanTest           = 42
    Deleted                = 44
    Thematic               = 66
    Vanilla                = 88

@public
class HoleType(enum.Enum):
    Normal = 0
    Blue   = 1
    Pink   = 2

    @classmethod
    def _missing_(cls, value):
        return cls.Normal

@public
class Currency(enum.Enum):
    Cheese = 0

    Unknown = -1

    @classmethod
    def _missing_(cls, value):
        return cls.Unknown

@public
class Trap(enum.Enum):
    Crusher       = 0
    Pendulum      = 1
    SwingingBlade = 2
    Acid          = 3
    Spikes        = 20
    Fire          = 21
    Snap          = 22
    SpinningBlade = 23

@public
class DeathType(enum.Enum):
    Normal          = 0
    CollisionDamage = 1
    NoBubbleSound   = 3

    Crushed     = 50
    Spiked      = 51
    Burned      = 52
    Decapitated = 53
    Dissolved   = 54
    Snapped     = 55
    Halved      = 56

    @classmethod
    def _missing_(cls, value):
        return cls.Normal

@public
class TradeError(enum.Enum):
    AlreadyInTrade    = 0
    TradeRejected     = 1
    TradeEnded        = 2
    DifferentRoom     = 3
    TradeCompleted    = 4
    ShamanCannotTrade = 5
    NotConnected      = 6
    InternalError     = 7

@public
class Trader(enum.Enum):
    Partner = 0
    Self    = 1
    Both    = 2

    @classmethod
    def _missing_(cls, value):
        return cls.Both

@public
class Bonus(enum.Enum):
    Point          = 0
    Speed          = 1
    Death          = 2
    Spring         = 3
    EasterEgg      = 4
    Booster        = 5
    Disintegration = 6

@public
class Monster(enum.Enum):
    # 'sq' is short for 'Squelette'.
    Skeleton = "sq"

    # 'f' is short for 'Fantome'.
    Ghost = "f"

    # 'Chat' is French for 'Cat'.
    SkeletonCat = "chat"

@public
class EventMapAction(enum.Enum):
    LightWind       = 1
    StartSailing    = 2
    HeavyWind       = 3
    LightRain       = 4
    HeavyRain       = 5
    SpawnBoat       = 6
    LightningStrike = 7

    SkeletonCatAttack = 10

@public
class ShamanMode(enum.Enum):
    Normal = 0
    Hard   = 1
    Divine = 2
