from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import List

class PlayerPrivate(BaseModel):
    player_name: str
    token: str

class EventType(Enum):
    VORBEHALT = "VORBEHALT"
    ABSAGE = "ABSAGE"
    KARTE = "KARTE"
    SERVER = "SERVER"
    CHAT = "CHAT"


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
    GAME_MODE = "GAME_MODE"
    WAIT_ANSAGE = "WAIT_ANSAGE"
    WAIT_PLAYERS = "WAIT_PLAYERS"
    PLAYER_JOINED = "PLAYER_JOINED"
    GAME_STARTED = "GAME_STARTED"


class Event(BaseModel):
    e_id: int = Field(default=None, example="42", description="Automatically set by server.")
    sender: str = Field(max_length=20, min_length=2, example="Herbert")
    e_type: EventType = Field(frozen=True, example="KARTE")
    content: Card | Absage | Vorbehalt | ServerMsg = Field(frozen=True, example="H10")
    add_data: str = Field(default=None, example="", description="Required for a few events, such as chat messages.")

    @model_validator(mode='after')
    def check_content_matches_event_type(self):
        if self.e_type == EventType.KARTE and type(self.content) != Card:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.ABSAGE and type(self.content) != Absage:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.VORBEHALT and type(self.content) != Vorbehalt:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.SERVER and type(self.content) != ServerMsg:
            raise ValueError('event type and content do not match')
        return self

class GameInfo(BaseModel):
    game_id: str = Field(default=None, example="fa4232", description="Game ID")
    round_counter: int = Field(example="3", description="The current round number (starting at 1)")
    players: List[str] = Field(example="[Herbert, Trudi, Werner, Doris]", description="Players in this game in game logical order.")