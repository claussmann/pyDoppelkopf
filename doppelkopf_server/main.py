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

@app.get("/api/{game_id}")
async def get_game_info(game_id) -> GameInfo:
    """
    Get game info such as players and round count.
    """
    ret = app.games[game_id].get_game_info()
    ret.game_id = game_id
    return ret

@app.post("/api/{game_id}/join")
def join(game_id, player_name:Annotated[str, Query(max_length=20, min_length=2, pattern="^[0-9A-Za-z\\-\\_]*$")]) -> PlayerPrivate:
    """
    Join the game with provided game id as player with the provided name.
    A player authentication token is returned, which is needed to perform
    actions as the player.
    """
    return app.games[game_id].join(player_name)

@app.get("/api/{game_id}/cards")
async def get_cards(game_id, player_name, player_token:str) -> List[Card]:
    """
    Get the cards the player has on the hand.
    Played cards will not appear here.
    """
    return app.games[game_id].get_cards(player_name, player_token)

@app.get("/api/{game_id}/event")
async def get_events(game_id, from_event_id:int=0) -> List[Event]:
    """
    Get all events in this game in chronological order.
    If provides, only events after the provided event id are returned.
    """
    return app.games[game_id].get_events(from_event_id)

@app.post("/api/{game_id}/event")
def new_event(game_id, player_token:str, event:Event) -> EventResponse:
    """
    Send a new event.
    The event will be validated, i.e. it is checked whether the action is legal.
    """
    ret = app.games[game_id].new_event(player_token, event)
    return EventResponse(successful=ret)
