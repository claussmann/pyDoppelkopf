from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from doppelkopf_server.game import Game
from doppelkopf_server.schemas import *
from typing import List, Annotated
import secrets

app = FastAPI()

app.mount("/ui", StaticFiles(directory="doppelkopf_server/frontend"), name="ui")

app.games = dict()

@app.get("/")
async def redirect_to_user_interface() -> GameInfo:
    """
    Forward to UI
    """
    return RedirectResponse("/ui/index.html")

@app.post("/api/new_game")
def new_game() -> GameCreatedInfo:
    """
    Creates a new game where players can join.
    The game is reachable by the game id returned on a successful call.
    """
    gid = str(secrets.token_hex(10))
    app.games[gid] = Game(gid)
    return GameCreatedInfo(game_id=gid)

@app.post("/api/{game_id}/join")
def join(game_id, player_name:Annotated[str, Query(max_length=20, min_length=2, pattern="^[0-9A-Za-z\\-\\_]*$")]) -> PlayerPrivate:
    """
    Join the game with provided game id as player with the provided name.
    A player authentication token is returned, which is needed to perform
    actions as the player.
    """
    return app.games[game_id].join(player_name)

@app.get("/api/{game_id}/playerinfo")
async def get_cards(game_id, player_token:str) -> PlayerPrivate:
    """
    Get the cards the player has on the hand.
    Played cards will not appear here.
    """
    return app.games[game_id].get_player_info(player_token)

@app.get("/api/{game_id}/event")
async def get_events(game_id, from_event_id:int=0) -> List[Event]:
    """
    Get all events in this game in chronological order.
    If provided, only events after the provided event id are returned.
    """
    return app.games[game_id].get_events(from_event_id)

@app.post("/api/{game_id}/lay_card")
def lay_card(game_id, player_token:str, card:Card) -> EventResponse:
    """
    Lay a card.
    """
    ret = app.games[game_id].process_card(player_token, card)
    return EventResponse(successful=ret)

@app.post("/api/{game_id}/say_vorbehalt")
def say_vorbehalt(game_id, player_token:str, vorbehalt:Vorbehalt) -> EventResponse:
    """
    Say a vorbehalt.
    """
    ret = app.games[game_id].process_vorbehalt(player_token, vorbehalt)
    return EventResponse(successful=ret)
