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
        self.round_cnt = 1
        self.active_round = None
        self.events = list()
        self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.SERVER, content=ServerMsg.WAIT_PLAYERS))


    def join(self, name):
        with self.mutex:
            if name in self.players_order or name == "Server":
                raise Exception("Name already exists.")
            if len(self.players) < 4:
                token = name + str(secrets.token_hex(10))
                self.players[token] = name
                self.players_order.append(name)
                self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.SERVER,
                                content=ServerMsg.PLAYER_JOINED, add_data=name))
                if len(self.players) == 4:
                    self.active_round = Runde(self.players_order[0], self.players_order[1], self.players_order[2], self.players_order[3], self.starter)
                    self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.SERVER, content=ServerMsg.GAME_STARTED))
                    self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.SERVER, content=ServerMsg.WAIT_ANSAGE, add_data=str(self.starter)))
                return PlayerPrivate(token=token, player_name=name)
            raise Exception("Game already full.")

    def get_events(self, from_e_id) -> List[Event]:
        return self.events[from_e_id:]

    def get_cards(self, token) -> List[Card]:
        if self.active_round != None:
            return self.active_round.get_hand(self.players[token])
        return list()

    def new_event(self, token, event) -> bool:
        if self.active_round != None:
            if not token in self.players:
                return False
            if not self.players[token] == event.sender:
                return False
            match event.e_type:
                case EventType.KARTE:
                    if self.active_round.new_card_event(event):
                        with self.mutex:
                            event.e_id = len(self.events)
                            self.events.append(event)
                        return True
        return False

    def get_game_info(self) -> GameInfo:
        return GameInfo(round_counter=self.round_cnt, players=self.players_order.copy())