import secrets
import random
from threading import Lock
from typing import List
from doppelkopf_server.schemas import *
from doppelkopf_server.enums import *
from doppelkopf_server.stich import *


class Game():
    def __init__(self):
        self.mutex = Lock()
        self.players = dict()
        self.round_cnt = 1
        self.active_round = None
        self.events = list()
        self.starter = 0
        self.game_mode = None
        self.current_stich = None
        self.state = GameState.WAIT_PLAYERS

    ##################################
    #### Non-Modifying methods #######
    ##################################

    def get_events(self, from_e_id) -> List[Event]:
        return self.events[from_e_id:]

    def get_cards(self, player_name, token) -> List[Card]:
        p = self._authenticate(token)
        return p.cards

    def get_game_info(self) -> GameInfo:
        players_public = [p.public() for p in self.players.values()]
        return GameInfo(round_counter=self.round_cnt, players=players_public)

    def get_player_info(self, token) -> PlayerPrivate:
        return self._authenticate(token)
    
    ##################################
    ###### Modifying methods #########
    ##################################

    def join(self, name) -> PlayerPrivate:
        with self.mutex:
            if len(self.players) < 4:
                p = PlayerPrivate(
                    name=name,
                    token=str(secrets.token_hex(10)),
                    position=len(self.players)
                )
                self.players[p.token] = p
                self._publish(Event(e_type=EventType.PLAYER_JOINED, content=p.public()))
                if len(self.players) == 4:
                    self._give_cards()
                    self._set_players_turn(self.starter)
                    self.state = GameState.WAIT_VORBEHALT
                return p
            raise Exception("Game already full.")
    
    def process_vorbehalt(self, token, vorbehalt) -> bool:
        with self.mutex:
            p = self._authenticate(token)
            if self.state != GameState.WAIT_VORBEHALT:
                return False
            if p.is_on_turn:
                p.vorbehalt = vorbehalt
            self.next_turn()
            if self._which_position_is_on_turn() == self.starter:
                vorbehalt, position = self._get_highest_vorbehalt_and_position()
                self.game_mode = vorbehalt
                self.starter = position
                self.current_stich = Stich(self.game_mode)
                self.state = GameState.ROUND_STARTED
            return True

    def process_card(self, token, card) -> bool:
        with self.mutex:
            p = self._authenticate(token)
            if not p.is_on_turn:
                return False
            if not card in p.cards:
                return False
            # TODO: Check if player is allowed to put the card (trumpf)
            p.cards.remove(card)
            self.current_stich.put_card(card)
            self._publish(Event(e_type=EventType.KARTE, content=KarteEvent(played_by=p.public(), card=card)))
            if self.current_stich.is_complete():
                winner_pos = self.current_stich.get_winner_position()
                self._get_player_by_position(winner_pos).stiche.append(self.current_stich)
                self.current_stich = Stich()
                # TODO: Check if round is over.
            else:
                self._next_turn()
            return True


    ##################################
    ####### Private Helpers ##########
    ##################################

    def _authenticate(self, token) -> PlayerPrivate:
        if token in self.players:
            return self.players[token]
        raise Exception("Token invalid.")
    
    def _publish(self, event):
        event.e_id = len(self.events)
        self.events.append(event)
    
    def _set_players_turn(self, position):
        for p in self.players.values():
            if p.position == position:
                p.is_on_turn = True
            else:
                p.is_on_turn = False
    
    def _next_turn(self):
        current_turn = self._which_position_is_on_turn()
        new_turn = (current_turn + 1) % 4
        self._set_players_turn(new_turn)
    
    def _which_position_is_on_turn(self) -> int:
        for p in self.players.values():
            if p.is_on_turn:
                return p.position
    
    def _get_player_by_position(self, position) -> PlayerPrivate:
        for p in self.players.values():
            if p.position == position:
                return p

    def _get_highest_vorbehalt_and_position(self):
        winner_pos = self.starter
        game_mode = self._get_player_by_position(winner_pos).vorbehalt
        for p in self.players.values():
            if p.vorbehalt.has_priority_over(game_mode):
                winner_pos = p.position
                game_mode = p.vorbehalt
        return (game_mode, winner_pos)

    def _give_cards(self):
        card_deck = [
            Card.D9, Card.D9, Card.DJ, Card.DJ, Card.DQ, Card.DQ,
            Card.DK, Card.DK, Card.D10, Card.D10, Card.DA, Card.DA,
            Card.H9, Card.H9, Card.HJ, Card.HJ, Card.HQ, Card.HQ,
            Card.HK, Card.HK, Card.H10, Card.H10, Card.HA, Card.HA,
            Card.S9, Card.S9, Card.SJ, Card.SJ, Card.SQ, Card.SQ,
            Card.SK, Card.SK, Card.S10, Card.S10, Card.SA, Card.SA,
            Card.C9, Card.C9, Card.CJ, Card.CJ, Card.CQ, Card.CQ,
            Card.CK, Card.CK, Card.C10, Card.C10, Card.CA, Card.CA
        ]
        for i in range(7):
            random.shuffle(card_deck)
        offset = 0
        for p in self.players.values():
            p.cards = card_deck[offset + 0 : offset + 12]
            offset += 12