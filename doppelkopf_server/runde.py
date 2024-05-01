import time
import random
import secrets
from threading import Lock
from doppelkopf_server.schemas import *



class Runde:
    def __init__(self, player_name_1: str, player_name_2: str, player_name_3: str, player_name_4: str, starter: int):
        self.mutex = Lock()
        if len({player_name_1, player_name_2, player_name_3, player_name_4}) < 4:
            Exception("Player names must be unique")
        self.card_deck = [
            Card.D9, Card.D9, Card.DJ, Card.DJ, Card.DQ, Card.DQ,
            Card.DK, Card.DK, Card.D10, Card.D10, Card.DA, Card.DA,
            Card.H9, Card.H9, Card.HJ, Card.HJ, Card.HQ, Card.HQ,
            Card.HK, Card.HK, Card.H10, Card.H10, Card.HA, Card.HA,
            Card.S9, Card.S9, Card.SJ, Card.SJ, Card.SQ, Card.SQ,
            Card.SK, Card.SK, Card.S10, Card.S10, Card.SA, Card.SA,
            Card.C9, Card.C9, Card.CJ, Card.CJ, Card.CQ, Card.CQ,
            Card.CK, Card.CK, Card.C10, Card.C10, Card.CA, Card.CA
        ]
        random.shuffle(self.card_deck)
        self.players = [player_name_1, player_name_2, player_name_3, player_name_4]
        self.table = {
            player_name_1: None,
            player_name_2: None,
            player_name_3: None,
            player_name_4: None
        }
        self.hands = {
            player_name_1: self.card_deck[0 : 12],
            player_name_2: self.card_deck[12 : 24],
            player_name_3: self.card_deck[24 : 36],
            player_name_4: self.card_deck[36 : 48]
        }
        self.current_turn = starter % 4
        self.stich_cnt = 0
        self.cards_in_stich = 0
        self.stiche = list()
        self.game_mode = Vorbehalt.GESUND
        self.game_mode_by = 0
        self.game_mode_by_name = None
        self.angesagt = 0

    def get_hand(self, player:str):
        if player in self.hands:
            return self.hands[player]
        raise Exception("Player Not Found")

    def ready_to_play(self) -> bool:
        return self.angesagt >= 4

    def get_current_turn_player(self) -> str:
        return self.players[self.current_turn]

    def get_game_mode(self) -> Vorbehalt:
        return self.game_mode

    def put_card(self, player:str, card:Card) -> bool:
        if not self.ready_to_play():
            return False
        if self.cards_in_stich >= 4:
            return False
        player_index = self.players.index(player)
        if self.current_turn == player_index:
            if card in self.hands[player]:
                with self.mutex:
                    self.hands[player].remove(card)
                    self.table[player] = card
                    self.current_turn = (self.current_turn + 1) % 4
                    self.cards_in_stich += 1
                return True
        return False

    def ansagen(self, player:str, vorbehalt:Vorbehalt) -> bool:
        if self.ready_to_play():
            return False
        player_index = self.players.index(player)
        if self.current_turn == player_index:
            if vorbehalt.has_priority_over(self.game_mode):
                with self.mutex:
                    self.game_mode = vorbehalt
                    self.game_mode_by = player_index
                    self.game_mode_by_name = player
                    self.angesagt += 1
                    self.current_turn = (self.current_turn + 1) % 4
                    if self.angesagt >= 4:
                        if vorbehalt.is_pflicht_solo():
                            self.current_turn = self.game_mode_by
                return True
        return False

    def is_stich_complete(self) -> bool:
        return self.cards_in_stich >= 4

    def process_stich(self) -> Stich:
        # TODO: Compute winner
        winner = self.players[0]
        stich = Stich(owner=winner, stich_counter=self.stich_cnt, cards=self.table.values())
        self.stiche.append(stich)
        for p in self.table.keys():
            self.table[p] = None
        self.cards_in_stich = 0
        self.stich_cnt += 1
        return stich

