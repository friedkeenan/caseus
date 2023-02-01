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
