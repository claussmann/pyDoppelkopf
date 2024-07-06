import time
from doppelkopf_server.schema import *
from pydantic import BaseModel


class Stich(BaseModel):
    cards_layed: dict[int,Card] = dict()
    index_started: int

    def put_card_by(self, player_pos:int, card:Card):
        if self.is_complete():
            raise Exception("Too many cards in Stich")
        self.cards_layed[player_pos] = card

    def is_complete(self) -> bool:
        return len(self.cards_layed) >= 4

    def get_winner(self, game_mode) -> int:
        if not self.is_complete():
            raise Exception("Winner can only be computed on complete Stichs")
        #
        # Determine what is trumpf
        spades_seq = [Card.SA, Card.S10, Card.SK, Card.SQ, Card.SJ, Card.S9]
        clubs_seq = [Card.CA, Card.C10, Card.CK, Card.CQ, Card.CJ, Card.C9]
        heart_seq = [Card.HA, Card.H10, Card.HK, Card.HQ, Card.HJ, Card.H9]
        diamond_seq = [Card.DA, Card.D10, Card.DK, Card.DQ, Card.DJ, Card.D9]
        match game_mode:
            # TODO
            case _:
                trumpf = [Card.SUPERSCHWEIN, Card.SCHWEIN, Card.H10,
                        Card.CQ, Card.SQ, Card.HQ, Card.DQ,
                        Card.CJ, Card.SJ, Card.HJ, Card.DJ,
                        Card.DA, Card.D10, Card.DK, Card.D9]
        #
        # Compute winner
        col_aufspiel = self.cards_layed[self.index_started].color()
        winner = self.index_started
        win_card = self.cards_layed[winner]
        for player_pos, card in self.cards_layed.items():
            if card in trumpf:
                if win_card in trumpf:
                    if trumpf.index(card) < trumpf.index(win_card):
                        win_card = card
                        winner = player_pos
                else:
                    win_card = card
                    winner = player_pos
            else:
                if not win_card in trumpf and card.color() == col_aufspiel:
                    match col_aufspiel:
                        case Card.DIAMOND:
                            if diamond_seq.index(card) < diamond_seq.index(win_card):
                                win_card = card
                                winner = player_pos
                        case Card.HEART:
                            if heart_seq.index(card) < heart_seq.index(win_card):
                                win_card = card
                                winner = player_pos
                        case Card.SPADES:
                            if spades_seq.index(card) < spades_seq.index(win_card):
                                win_card = card
                                winner = player_pos
                        case Card.CLUBS:
                            if clubs_seq.index(card) < clubs_seq.index(win_card):
                                win_card = card
                                winner = player_pos
        return winner
