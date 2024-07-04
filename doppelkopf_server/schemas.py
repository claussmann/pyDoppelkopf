from pydantic import BaseModel, Field, model_validator
from typing import List
from doppelkopf_server.schemas import *
from doppelkopf_server.enums import *
from doppelkopf_server.stich import Stich

class PlayerPrivate(BaseModel):
    position: int
    name: str
    token: str
    points: int = 0
    is_on_turn: bool = False
    cards: List[Card] = list()
    vorbehalt: Vorbehalt = None
    stiche: List[Stich] = list()

    def public(self):
        v = self.vorbehalt
        if v != Vorbehalt.GESUND:
            v = Vorbehalt.HIDDEN
        return PlayerPublic(
            position=self.position,
            name = self.name,
            is_on_turn=self.is_on_turn,
            vorbehalt=v
        )

class PlayerPublic(BaseModel):
    position: int
    name: str
    is_on_turn: bool
    vorbehalt: Vorbehalt

class KarteEvent(BaseModel):
    played_by: PlayerPublic
    card: Card

class VorbehaltEvent(BaseModel):
    said_by: PlayerPublic
    vorbehalt: Vorbehalt

class EventResponse(BaseModel):
    successful: bool

class EventType(Enum):
    VORBEHALT = "VORBEHALT"
    KARTE = "KARTE"
    PLAYER_JOINED = "PLAYER_JOINED"
    STICH = "STICH"

    def is_server_privilege(self):
        return self is not EventType.KARTE

class Event(BaseModel):
    e_id: int = Field(default=None, description="Automatically set by server.")
    e_type: EventType = Field(frozen=True)
    content: KarteEvent | VorbehaltEvent | PlayerPublic = Field(frozen=True, default=None)

    @model_validator(mode='after')
    def check_content_matches_event_type(self):
        if self.e_type == EventType.KARTE and type(self.content) != KarteEvent:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.VORBEHALT and type(self.content) != VorbehaltEvent:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.PLAYER_JOINED and type(self.content) != PlayerPublic:
            raise ValueError('event type and content do not match')
        return self

class GameInfo(BaseModel):
    game_id: str = Field(default=None, description="Game ID")
    round_counter: int = Field(description="The current round number (starting at 1)")
    players: List[PlayerPublic] = Field(description="Players in this game in game logical order.")
