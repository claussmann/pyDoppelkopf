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
        self.players_points = dict()
        self.players_solos = dict()
        self.starter = 0
        self.round_cnt = 1
        self.active_round = None
        self.events = list()
        self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.WAIT_PLAYERS))


    def join(self, name):
        with self.mutex:
            if name in self.players_order or name == "Server":
                raise Exception("Name already exists.")
            if len(self.players) < 4:
                token = name + str(secrets.token_hex(10))
                self.players[token] = name
                self.players_order.append(name)
                self.players_points[name] = 0
                self.players_solos[name] = 0
                self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.PLAYER_JOINED, text_content=name))
                if len(self.players) == 4:
                    self._new_round()
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
            if event.e_type.is_server_privilege():
                return False
            match event.e_type:
                case EventType.KARTE:
                    return self._process_card_event(event)
                case EventType.VORBEHALT:
                    return self._process_vorbehalt_event(event)
        return False

    def get_game_info(self) -> GameInfo:
        return GameInfo(round_counter=self.round_cnt, players=self.players_order.copy())




    ##################################
    ####### Private Helpers ##########
    ##################################

    def _new_round(self):
        self.active_round = Runde(self.players_order[0], self.players_order[1], self.players_order[2], self.players_order[3], self.starter)
        self.events.append(Event(e_id=len(self.events), sender="Server", e_type=EventType.WAIT_VORBEHALT,
                            text_content=self.active_round.get_current_turn_player()))
        self.starter = (self.starter + 1) % 4

    def _process_card_event(self, event):
        if self.active_round.put_card(event.sender, event.content):
            with self.mutex:
                event.e_id = len(self.events)
                self.events.append(event)
            if self.active_round.is_stich_complete():
                stich = self.active_round.process_stich()
                with self.mutex:
                    stich_event = Event(e_id=len(self.events), sender="Server", e_type=EventType.STICH, content=stich)
                    self.events.append(stich_event)
            return True
        return False

    def _process_vorbehalt_event(self, event):
        if event.content.is_pflicht_solo() and self.players_solos[event.sender] > 0:
            return False # Pflichtsolo can only be played once.
        if self.active_round.ansagen(event.sender, event.content):
            with self.mutex:
                event.e_id = len(self.events)
                self.events.append(event)
                if self.active_round.ready_to_play():
                    self.events.append(
                        Event(e_id=len(self.events), sender="Server", e_type=EventType.GAME_MODE, content=self.active_round.get_game_mode())
                    )
                    self.events.append(
                        Event(e_id=len(self.events), sender="Server", e_type=EventType.ROUND_STARTED, text_content=self.active_round.get_current_turn_player())
                    )
                    if event.content.is_solo():
                        self.players_solos[event.sender] += 1
            return True
