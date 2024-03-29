from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from doppelkopf_server.game import Game
from doppelkopf_server.schemas import *
from typing import List, Annotated
import secrets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.games = dict()


@app.post("/new_game")
def new_game() -> GameInfo:
    """
    Creates a new game where players can join.
    The game is reachable by the game id returned on a successful call.
    """
    gid = str(secrets.token_hex(6))
    app.games[gid] = Game()
    ret = app.games[gid].get_game_info()
    ret.game_id = gid
    return ret

@app.get("/{game_id}")
async def get_game_info(game_id) -> GameInfo:
    """
    Get game info such as players and round count.
    """
    ret = app.games[game_id].get_game_info()
    ret.game_id = game_id
    return ret

@app.post("/{game_id}/join")
def join(game_id, player_name:Annotated[str, Query(max_length=20, min_length=2, pattern="^[0-9A-Za-z\-\_]*$")]) -> PlayerPrivate:
    """
    Join the game with provided game id as player with the provided name.
    A player authentication token is returned, which is needed to perform
    actions as the player.
    """
    return app.games[game_id].join(player_name)

@app.get("/{game_id}/cards")
async def get_cards(game_id, player_token:str) -> List[Card]:
    """
    Get the cards the player has on the hand.
    Played cards will not appear here.
    """
    return app.games[game_id].get_cards(player_token)

@app.get("/{game_id}/event")
async def get_events(game_id, from_event_id:int=0) -> List[Event]:
    """
    Get all events in this game in chronological order.
    If provides, only events after the provided event id are returned.
    """
    return app.games[game_id].get_events(from_event_id)

@app.post("/{game_id}/event")
def new_event(game_id, player_token:str, event:Event) -> bool:
    """
    Send a new event.
    The event will be validated, i.e. it is checked whether the action is legal.
    """
    return app.games[game_id].new_event(player_token, event)