from pydantic import BaseModel, Field, model_validator
from typing import List
from enum import Enum
from doppelkopf_server.player import PlayerPublic
from doppelkopf_server.schema import Card, Vorbehalt, GameState

class GameStatusEvent(BaseModel):
    game_id: str = Field(default=None, description="Game ID")
    round_counter: int = Field(description="The current round number (starting at 1)")
    state: GameState
    mode: Vorbehalt = Field(default=None, description="The Vorbehalt which is active")
    whose_turn: int

class KarteEvent(BaseModel):
    played_by: PlayerPublic
    card: Card

class VorbehaltEvent(BaseModel):
    said_by: PlayerPublic
    vorbehalt: Vorbehalt

class EventType(Enum):
    VORBEHALT = "VORBEHALT"
    KARTE = "KARTE"
    PLAYER_JOINED = "PLAYER_JOINED"
    STICH = "STICH"
    GAME_STATE_CHANGED = "GAME_STATE_CHANGED"

class Event(BaseModel):
    e_id: int = Field(default=None, description="Automatically set by server.")
    e_type: EventType = Field(frozen=True)
    content: KarteEvent | VorbehaltEvent | PlayerPublic | GameStatusEvent = Field(frozen=True, default=None)

    @model_validator(mode='after')
    def check_content_matches_event_type(self):
        if self.e_type == EventType.GAME_STATE_CHANGED and type(self.content) != GameStatusEvent:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.KARTE and type(self.content) != KarteEvent:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.VORBEHALT and type(self.content) != VorbehaltEvent:
            raise ValueError('event type and content do not match')
        if self.e_type == EventType.PLAYER_JOINED and type(self.content) != PlayerPublic:
            raise ValueError('event type and content do not match')
        return self

