import time
from doppelkopf_server.schemas import *
from pydantic import BaseModel, Field, model_validator


class Stich(BaseModel):
    def __init__(self, game_mode: Vorbehalt):
        self.cards_layed = list()
        self.spades_seq = [Card.SA, Card.S10, Card.SK, Card.SQ, Card.SJ, Card.S9]
        self.cross_seq = [Card.CA, Card.C10, Card.CK, Card.CQ, Card.CJ, Card.C9]
        self.heart_seq = [Card.HA, Card.H10, Card.HK, Card.HQ, Card.HJ, Card.H9]
        self.diamond_seq = [Card.DA, Card.D10, Card.DK, Card.DQ, Card.DJ, Card.D9]
        match game_mode:
            case Vorbehalt.FLEISCHLOSER:
                self.trumpf = list()
            case Vorbehalt.DAMENSOLO:
                self.trumpf = [Card.CQ, Card.SQ, Card.HQ, Card.DQ]
            case Vorbehalt.BUBENSOLO:
                self.trumpf = [Card.CJ, Card.SJ, Card.HJ, Card.DJ]
            # TODO: Weitere Cases
            case _:
                self.trumpf = [Card.SUPERSCHWEIN, Card.SCHWEIN, Card.H10,
                        Card.CQ, Card.SQ, Card.HQ, Card.DQ,
                        Card.CJ, Card.SJ, Card.HJ, Card.DJ,
                        Card.DA, Card.D10, Card.DK, Card.D9]

    def put_card_by(self, player:str, card:Card):
        if self.is_complete():
            raise Exception("Too many cards in Stich")
        self.cards_layed.append((player, card))

    def is_complete(self) -> bool:
        return len(self.cards_layed) >= 4

    def get_winner(self) -> str:
        if not self.is_complete():
            raise Exception("Winner can only be computed on complete Stichs")
        col_aufspiel = self.cards_layed[0][1].color()
        winner = self.cards_layed[0][0]
        win_card = self.cards_layed[0][1]
        for player, card in self.cards_layed:
            if card in self.trumpf:
                if win_card in self.trumpf:
                    if self.trumpf.index(card) < self.trumpf.index(win_card):
                        win_card = card
                        winner = player
                else:
                    win_card = card
                    winner = player
            else:
                if not win_card in self.trumpf and card.color() == col_aufspiel:
                    match col_aufspiel:
                        case Card.DIAMOND:
                            if self.diamond_seq.index(card) < self.diamond_seq.index(win_card):
                                win_card = card
                                winner = player
                        case Card.HEART:
                            if self.heart_seq.index(card) < self.heart_seq.index(win_card):
                                win_card = card
                                winner = player
                        case Card.SPADES:
                            if self.spades_seq.index(card) < self.spades_seq.index(win_card):
                                win_card = card
                                winner = player
                        case Card.CLUBS:
                            if self.clubs_seq.index(card) < self.clubs_seq.index(win_card):
                                win_card = card
                                winner = player
        return winner
