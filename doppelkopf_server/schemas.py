from pydantic import BaseModel, Field
from enum import Enum


class EventType(Enum):
    VORBEHALT = "VORBEHALT"
    ABSAGE = "ABSAGE"
    KARTE = "KARTE"
    SERVER = "SERVER"


class Card(Enum):
    # Diamonds
    D9 = "D9"
    DJ = "DJ"
    DD = "DD"
    DK = "DK"
    D10 = "D10"
    DA = "DA"

    # Heart
    H9 = "H9"
    HJ = "HJ"
    HD = "HD"
    HK = "HK"
    H10 = "H10"
    HA = "HA"

    # Spades
    S9 = "S9"
    SJ = "SJ"
    SD = "SD"
    SK = "SK"
    S10 = "S10"
    SA = "SA"

    # Clubs
    C9 = "C9"
    CJ = "CJ"
    CD = "CD"
    CK = "CK"
    C10 = "C10"
    CA = "CA"

    def is_diamond(self):
        dia = [Card.D9, Card.DK, Card.DJ, Card.DD, Card.D10, Card.DA]
        return self in dia

    def is_heart(self):
        hearts = [Card.H9, Card.HK, Card.HJ, Card.HD, Card.H10, Card.HA]
        return self in hearts

    def is_spades(self):
        spades = [Card.S9, Card.SK, Card.SJ, Card.SD, Card.S10, Card.SA]
        return self in spades

    def is_cross(self):
        cross = [Card.C9, Card.CK, Card.CJ, Card.CD, Card.C10, Card.CA]
        return self in cross

    def counting_value(self):
        if self in [Card.DJ, Card.HJ, Card.CJ, Card.SJ]:
            return 2
        if self in [Card.DD, Card.HD, Card.CD, Card.SD]:
            return 3
        if self in [Card.DK, Card.HK, Card.CK, Card.SK]:
            return 4
        if self in [Card.D10, Card.H10, Card.C10, Card.S10]:
            return 10
        if self in [Card.DA, Card.HA, Card.CA, Card.SA]:
            return 11
        return 0


class Vorbehalt(Enum):
    GESUND = "GESUND"
    HOCHZEIT = "HOCHZEIT"
    ARMUT = "ARMUT"
    SOLO = "SOLO"
    FLEISCHLOSER = "FLEISCHLOSER"
    BUBENSOLO = "BUBENSOLO"
    DAMENSOLO = "DAMENSOLO"
    FARBSOLO_DIAMOND = "FARBSOLO_DIAMOND"
    FARBSOLO_HEART = "FARBSOLO_HEART"
    FARBSOLO_CROSS = "FARBSOLO_CROSS"
    FARBSOLO_SPADES = "FARBSOLO_SPADES"

    def is_solo(self):
        return self in [Vorbehalt.SOLO, Vorbehalt.FLEISCHLOSER,
                    Vorbehalt.BUBENSOLO, Vorbehalt.DAMENSOLO]

    def has_priority_over(self, other):
        priority = [Vorbehalt.SOLO, Vorbehalt.FLEISCHLOSER, Vorbehalt.BUBENSOLO, Vorbehalt.DAMENSOLO]
        if other not in priority:
            return True
        return priority.index(self) > priority.index(other)


class Absage(Enum):
    RE_WINS = "RE_WINS"
    KONTRA_WINS = "KONTRA_WINS"


class ServerMsg(Enum):
    CHAT = "CHAT"
    GAME_MODE = "GAME_MODE"
    WAIT_ANSAGE = "WAIT_ANSAGE"


class Event(BaseModel):
    event_id: int = Field(default=None, example="42", description="Automatically set by server.")
    player_name: str = Field(max_length=20, min_length=2, example="Herbert")
    event_type: EventType = Field(frozen=True, example="KARTE")
    content: Card | Absage | Vorbehalt | ServerMsg = Field(frozen=True, example="H10")
    additional_data: str = Field(default=None, example="", description="Required for a few events, such as chat messages.")