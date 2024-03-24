import secrets
from threading import Lock
from typing import List
from doppelkopf_server.schemas import *
from doppelkopf_server.runde import *


class Game():
    def __init__(self):
        self.mutex = Lock()
        self.players = dict()
        self.players_order = list()
        self.starter = 0
        self.active_round = None

    def join(self, name):
        with self.mutex:
            if name in self.players_order or name == "Server":
                raise Exception("Name already exists.")
            if len(self.players) < 4:
                token = name + "t" #str(secrets.token_hex(10))
                self.players[token] = name
                self.players_order.append(name)
                if len(self.players) == 4:
                    self.active_round = Runde(self.players_order[0], self.players_order[1], self.players_order[2], self.players_order[3])
                return token
            raise Exception("Game already full.")

    def get_events(self, from_event_id) -> List[Event]:
        if self.active_round != None:
            return self.active_round.get_events(from_event_id)
        return list()

    def get_cards(self, token) -> List[Card]:
        if self.active_round != None:
            return self.active_round.get_hand(self.players[token])
        return list()

    def new_event(self, token, event) -> bool:
        if self.active_round != None:
            # TODO: Validate Player token.
            return self.active_round.new_event(event)
        return False