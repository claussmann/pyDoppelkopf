from doppelkopf_server.stich import *
from doppelkopf_server.game import *


def test_stich_complete():
    stich = Stich(index_started=0)
    stich.put_card_by(0, Card.HK)
    assert not stich.is_complete()
    stich.put_card_by(1, Card.H9)
    stich.put_card_by(2, Card.H9)
    stich.put_card_by(3, Card.H10)
    assert stich.is_complete()

def test_stich_winner_normal_game_fehl():
    stich = Stich(index_started=1)
    stich.put_card_by(1, Card.HK)
    stich.put_card_by(2, Card.H9)
    stich.put_card_by(3, Card.HA)
    stich.put_card_by(0, Card.HA)
    assert stich.get_winner(Vorbehalt.GESUND) == 3

def test_stich_winner_normal_game_fehl_abwurf():
    stich = Stich(index_started=0)
    stich.put_card_by(0, Card.HA)
    stich.put_card_by(1, Card.H9)
    stich.put_card_by(2, Card.HA)
    stich.put_card_by(3, Card.C9)
    assert stich.get_winner(Vorbehalt.GESUND) == 0

def test_stich_winner_normal_game_trumpf():
    stich = Stich(index_started=2)
    stich.put_card_by(2, Card.HA)
    stich.put_card_by(3, Card.SQ)
    stich.put_card_by(0, Card.H9)
    stich.put_card_by(1, Card.H9)
    assert stich.get_winner(Vorbehalt.GESUND) == 3

def test_stich_winner_normal_game_trumpf_aufspiel():
    stich = Stich(index_started=1)
    stich.put_card_by(1, Card.D10)
    stich.put_card_by(2, Card.CJ)
    stich.put_card_by(3, Card.SQ)
    stich.put_card_by(0, Card.D9)
    assert stich.get_winner(Vorbehalt.GESUND) == 3
