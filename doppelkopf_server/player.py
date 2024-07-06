from pydantic import BaseModel
from typing import List
from doppelkopf_server.schema import Card, Vorbehalt
from doppelkopf_server.stich import Stich

class PlayerPrivate(BaseModel):
    position: int
    name: str
    token: str
    points: int = 0
    is_on_turn: bool = False
    cards: List[Card] = list()
    vorbehalt: Vorbehalt = Vorbehalt.PENDING
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