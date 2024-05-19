import secrets
from threading import Lock
from typing import List
from doppelkopf_server.schemas import *
from doppelkopf_server.runde import *
from doppelkopf_server.vorbehaltmanager import *


class Game():
    def __init__(self):
        self.mutex = Lock()
        self.players = list()
        self.players_tokens = dict()
        self.players_points = dict()
        self.starter = 0
        self.round_cnt = 1
        self.active_round = None
        self.events = list()
        self._publish(Event(sender="Server", e_type=EventType.WAIT_PLAYERS))


    def join(self, name):
        with self.mutex:
            if name in self.players or name == "Server":
                raise Exception("Name already exists.")
            if len(self.players) < 4:
                token = name + str(secrets.token_hex(10))
                self.players_tokens[name] = token
                self.players.append(name)
                self.players_points[name] = 0
                self._publish(Event(sender="Server", e_type=EventType.PLAYER_JOINED, text_content=name))
                if len(self.players) == 4:
                    self.active_round = Runde(
                        self.players[self.starter],
                        self.players[(self.starter + 1) % 4],
                        self.players[(self.starter + 2) % 4],
                        self.players[(self.starter + 3) % 4]
                    )
                    self._publish(Event(sender="Server", e_type=EventType.WAIT_VORBEHALT, text_content=self.players[self.starter]))
                return PlayerPrivate(token=token, player_name=name)
            raise Exception("Game already full.")

    def get_events(self, from_e_id) -> List[Event]:
        return self.events[from_e_id:]

    def get_cards(self, player_name, token) -> List[Card]:
        if self.active_round != None:
            if player_name in self.players and self.players_tokens[player_name] == token:
                return self.active_round.get_hand(player_name)
        return list()

    def new_event(self, token, event) -> bool:
        if not event.sender in self.players:
            return False
        if not self.players_tokens[event.sender] == token:
            return False
        if event.e_type.is_server_privilege():
            return False
        with self.mutex:
            if not self.active_round == None:
                match event.e_type:
                    case EventType.KARTE:
                        return self._process_card_event(event)
                    case EventType.VORBEHALT:
                        return self._process_vorbehalt_event(event)
        return False

    def get_game_info(self) -> GameInfo:
        return GameInfo(round_counter=self.round_cnt, players=self.players.copy())




    ##################################
    ####### Private Helpers ##########
    ##################################
    def _publish(self, event):
        event.e_id = len(self.events)
        self.events.append(event)

    def _process_card_event(self, event):
        if self.active_round.put_card(event.sender, event.content):
            event.e_id = len(self.events)
            self.events.append(event)
            return True
        return False

    def _process_vorbehalt_event(self, event):
        if self.active_round.put_vorbehalt(event.sender, event.content):
            event.e_id = len(self.events)
            self.events.append(event)
            if self.active_round.ready_to_play():
                self._publish(Event(sender="Server", e_type=EventType.GAME_MODE, content=self.active_round.get_game_mode()))
                self._publish(Event(sender="Server", e_type=EventType.ROUND_STARTED, text_content=self.active_round.get_current_turn_player()))
            return True
        return False
