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
