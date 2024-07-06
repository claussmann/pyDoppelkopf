import secrets
import random
from threading import Lock
from typing import List
from doppelkopf_server.player import *
from doppelkopf_server.event import *
from doppelkopf_server.schema import *
from doppelkopf_server.stich import *


class Game():
    def __init__(self, id:str):
        self.mutex = Lock()
        self.id = id
        self.players = dict()
        self.round_cnt = 1
        self.events = list()
        self.starter = 0
        self.game_mode = Vorbehalt.PENDING
        self.current_stich = None
        self._set_state(GameState.WAIT_PLAYERS)

    ##################################
    #### Non-Modifying methods #######
    ##################################

    def get_events(self, from_e_id) -> List[Event]:
        return self.events[from_e_id:]

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
                self._notify_event(EventType.PLAYER_JOINED, p.public())
                if len(self.players) == 4:
                    self._give_cards()
                    self._set_players_turn(self.starter)
                    self._set_state(GameState.WAIT_VORBEHALT)
                return p
            raise Exception("Game already full.")
    
    def process_vorbehalt(self, token, vorbehalt) -> bool:
        with self.mutex:
            p = self._authenticate(token)
            if self.state != GameState.WAIT_VORBEHALT:
                return False
            if not p.is_on_turn:
                return False
            p.vorbehalt = vorbehalt
            self._next_turn()
            v_event = VorbehaltEvent(said_by=p.public(), vorbehalt=vorbehalt)
            self._notify_event(EventType.VORBEHALT, v_event)
            if self._which_position_is_on_turn() == self.starter:
                vorbehalt, position = self._get_highest_vorbehalt_and_position()
                self.game_mode = vorbehalt
                self.starter = position
                self.current_stich = Stich(index_started=self.starter)
                self._set_state(GameState.ROUND_STARTED)
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
            self.current_stich.put_card_by(p.position, card)
            self._notify_event(EventType.KARTE, KarteEvent(played_by=p.public(), card=card))
            if self.current_stich.is_complete():
                winner_pos = self.current_stich.get_winner(self.game_mode)
                self._get_player_by_position(winner_pos).stiche.append(self.current_stich)
                self.current_stich = Stich(index_started=winner_pos)
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
    
    def _notify_event(self, etype:EventType, econtent):
        e = Event(e_id=len(self.events), e_type=etype, content=econtent)
        self.events.append(e)
    
    def _set_players_turn(self, position:int):
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
        return -1
    
    def _get_player_by_position(self, position:int) -> PlayerPrivate:
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

    def _set_state(self, state:GameState):
        self.state = state
        info = GameStatusEvent(game_id=self.id, 
                        round_counter=self.round_cnt, 
                        state=self.state,
                        mode=self.game_mode,
                        whose_turn=self._which_position_is_on_turn())
        self._notify_event(EventType.GAME_STATE_CHANGED, info)

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