import time
import random
import secrets
from doppelkopf_server.schemas import *
from doppelkopf_server.stich import *



class Runde:
    """
    Player names in the order of play. First player starts game round.
    """
    def __init__(self, pname1: str, pname2: str, pname3: str, pname4: str):
        if len({pname1, pname2, pname3, pname4}) < 4:
            Exception("Player names must be unique")
        self.players = [pname1, pname2, pname3, pname4]
        self.game_mode = None
        self.vorbehaltmanager = VorbehaltManager()
        self._give_cards()
        self.current_turn = 0
        self.stiche = list()

    def get_hand(self, player:str):
        if player in self.hands:
            return self.hands[player]
        raise Exception("Player Not Found")

    def get_current_turn_player(self) -> str:
        return self.players[self.current_turn]

    def get_game_mode(self) -> Vorbehalt:
        return self.game_mode

    def ready_to_play(self) -> bool:
        return self.game_mode is not None

    def put_vorbehalt(self, player: str, vorbehalt: Vorbehalt) -> bool:
        if self.game_mode is not None:
            return False
        if not self.get_current_turn_player() == player:
            return False
        self.vorbehaltmanager.new_vorbehalt(player, vorbehalt)
        self.current_turn = (self.current_turn + 1) % 4
        if self.vorbehaltmanager.is_ready():
            by_whom, game_mode = self.vorbehaltmanager.evaluate()
            self.game_mode = game_mode
            self.current_turn = self.players.index(by_whom)
            self.stiche.append(Stich(game_mode))
        return True

    def put_card(self, player:str, card:Card) -> bool:
        if self.get_current_turn_player() == player and self.ready_to_play():
            if card in self.hands[player]:
                # TODO: Check if player is allowed to put the card (trumpf)
                self.hands[player].remove(card)
                current_stich = self.stiche[-1]
                current_stich.put_card_by(player, card)
                if current_stich.is_complete():
                    winner = current_stich.get_winner()
                    self.current_turn = self.players.index(winner)
                else:
                    self.current_turn = (self.current_turn + 1) % 4
                return True
        return False

    def _give_cards(self):
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
        for i in range(7):
            random.shuffle(self.card_deck)
        self.hands = {
            self.players[0]: self.card_deck[0 : 12],
            self.players[1]: self.card_deck[12 : 24],
            self.players[2]: self.card_deck[24 : 36],
            self.players[3]: self.card_deck[36 : 48]
        }
        # TODO: Check for Schwein etc.


class VorbehaltManager:
    def __init__(self):
        self.vorbehalte = list()

    def new_vorbehalt(self, player: str, vorbehalt: Vorbehalt):
        for p, v in self.vorbehalte:
            if p == player:
                return # TODO: Error handling
        self.vorbehalte.append((player, vorbehalt))

    def is_ready(self):
        return len(self.vorbehalte) == 4

    def evaluate(self) -> (str, Vorbehalt):
        winner = self.vorbehalte[0][0]
        game_mode = self.vorbehalte[0][1]
        for player, vorbehalt in self.vorbehalte:
            if vorbehalt.has_priority_over(game_mode):
                winner = player
                game_mode = vorbehalt
        return (winner, game_mode)
