from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import List

class PlayerPrivate(BaseModel):
    player_name: str
    token: str

class EventResponse(BaseModel):
    successful: bool

class EventType(Enum):
    VORBEHALT = "VORBEHALT"
    ABSAGE = "ABSAGE"
    KARTE = "KARTE"
    SERVER = "SERVER"
    CHAT = "CHAT"
    GAME_MODE = "GAME_MODE"
    WAIT_VORBEHALT = "WAIT_VORBEHALT"
    WAIT_PLAYERS = "WAIT_PLAYERS"
    PLAYER_JOINED = "PLAYER_JOINED"
    ROUND_STARTED = "ROUND_STARTED"
    STICH = "STICH"

    def is_server_privilege(self):
        return self in [EventType.GAME_MODE, EventType.WAIT_VORBEHALT, EventType.WAIT_PLAYERS,
                    EventType.PLAYER_JOINED, EventType.ROUND_STARTED, EventType.STICH]


class Card(Enum):
    # Special
    SCHWEIN = "SCHWEIN"; SUPERSCHWEIN = "SUPERSCHWEIN"
    # Diamonds
    D9 = "D9"; DJ = "DJ"; DQ = "DQ"; DK = "DK"; D10 = "D10"; DA = "DA"
    # Heart
    H9 = "H9"; HJ = "HJ"; HQ = "HQ"; HK = "HK"; H10 = "H10"; HA = "HA"
    # Spades
    S9 = "S9"; SJ = "SJ"; SQ = "SQ"; SK = "SK"; S10 = "S10"; SA = "SA"
    # Clubs
    C9 = "C9"; CJ = "CJ"; CQ = "CQ"; CK = "CK"; C10 = "C10"; CA = "CA"

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
    SCHMEISSEN = "SCHMEISSEN"
    #
    SOLO = "SOLO"
    FLEISCHLOSER = "FLEISCHLOSER"
    BUBENSOLO = "BUBENSOLO"
    DAMENSOLO = "DAMENSOLO"
    FARBSOLO_DIAMOND = "FARBSOLO_DIAMOND"
    FARBSOLO_HEART = "FARBSOLO_HEART"
    FARBSOLO_CLUBS = "FARBSOLO_CLUBS"
    FARBSOLO_SPADES = "FARBSOLO_SPADES"
    #
    PFLICHT_SOLO = "PFLICHT_SOLO"
    PFLICHT_FLEISCHLOSER = "PFLICHT_FLEISCHLOSER"
    PFLICHT_BUBENSOLO = "PFLICHT_BUBENSOLO"
    PFLICHT_DAMENSOLO = "PFLICHT_DAMENSOLO"
    PFLICHT_FARBSOLO_DIAMOND = "PFLICHT_FARBSOLO_DIAMOND"
    PFLICHT_FARBSOLO_HEART = "PFLICHT_FARBSOLO_HEART"
    PFLICHT_FARBSOLO_CLUBS = "PFLICHT_FARBSOLO_CLUBS"
    PFLICHT_FARBSOLO_SPADES = "PFLICHT_FARBSOLO_SPADES"

    def is_solo(self):
        return self not in [Vorbehalt.GESUND, Vorbehalt.HOCHZEIT, Vorbehalt.ARMUT, Vorbehalt.SCHMEISSEN]

    def is_pflicht_solo(self):
        return self in [Vorbehalt.PFLICHT_SOLO, Vorbehalt.PFLICHT_FLEISCHLOSER, Vorbehalt.PFLICHT_BUBENSOLO,
                        Vorbehalt.PFLICHT_DAMENSOLO, Vorbehalt.PFLICHT_FARBSOLO_DIAMOND, Vorbehalt.PFLICHT_FARBSOLO_HEART,
                        Vorbehalt.PFLICHT_FARBSOLO_CLUBS, Vorbehalt.PFLICHT_FARBSOLO_SPADES]

    def has_priority_over(self, other):
        if other == Vorbehalt.SCHMEISSEN:
            return False
        if self.is_pflicht_solo():
            return True
        if other.is_pflicht_solo():
            return False
        if self.is_solo():
            return True
        if other.is_solo():
            return False
        if self == Vorbehalt.ARMUT:
            return True
        if self == Vorbehalt.HOCHZEIT and other != Vorbehalt.ARMUT:
            return True
        if self == Vorbehalt.GESUND and other != Vorbehalt.GESUND:
            return False
        return True


class Absage(Enum):
    RE_WINS = "RE_WINS"
    KONTRA_WINS = "KONTRA_WINS"


class Event(BaseModel):
    e_id: int = Field(default=None, description="Automatically set by server.")
    sender: str = Field(max_length=20, min_length=2)
    e_type: EventType = Field(frozen=True)
    content: Card | Absage | Vorbehalt = Field(frozen=True, default=None)
    text_content: str = Field(frozen=True, default="", max_length=150)

    @model_validator(mode='after')
    def check_content_matches_event_type(self):
        if self.e_type == EventType.KARTE and type(self.content) != Card:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.ABSAGE and type(self.content) != Absage:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.VORBEHALT and type(self.content) != Vorbehalt:
            raise ValueError('event type and content do not match')
        return self

class GameInfo(BaseModel):
    game_id: str = Field(default=None, description="Game ID")
    round_counter: int = Field(description="The current round number (starting at 1)")
    players: List[str] = Field(description="Players in this game in game logical order.")