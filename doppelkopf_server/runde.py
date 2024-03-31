import time
import random
import secrets
from threading import Lock
from doppelkopf_server.schemas import *



class Runde:
    def __init__(self, player_name_1: str, player_name_2: str, player_name_3: str, player_name_4: str, starter: int):
        self.mutex = Lock()
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
        self.hands = list()
        for i in range(4):
            self.hands.append(self.card_deck[12*(i) : 12*(i+1)])
        self.current_turn = starter % 4

    def get_hand(self, player_name):
        if player_name in self.players:
            return self.hands[self.players.index(player_name)]
        raise Exception("Player Not Found")

    def new_card_event(self, event: Event) -> bool:
        player_index = self.players.index(event.sender)
        if self.current_turn == player_index:
            card = event.content
            if card in self.hands[player_index]:
                with self.mutex:
                    self.hands[player_index].remove(card)
                    self.current_turn = (self.current_turn + 1) % 4
                return True
        return False



