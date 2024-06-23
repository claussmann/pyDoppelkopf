import pytest
from doppelkopf_server.stich import *
from doppelkopf_server.schemas import *

def test_stich_trumpf_computed_correctly():
    stich = Stich(Vorbehalt.GESUND)
    assert stich.trumpf == [Card.SUPERSCHWEIN, Card.SCHWEIN, Card.H10,
                        Card.CQ, Card.SQ, Card.HQ, Card.DQ,
                        Card.CJ, Card.SJ, Card.HJ, Card.DJ,
                        Card.DA, Card.D10, Card.DK, Card.D9]
    stich = Stich(Vorbehalt.BUBENSOLO)
    assert stich.trumpf == [Card.CJ, Card.SJ, Card.HJ, Card.DJ]

def test_stich_complete():
    stich = Stich(Vorbehalt.GESUND)
    stich.put_card_by("Peter", Card.HK)
    assert not stich.is_complete()
    stich.put_card_by("Günter", Card.H9)
    stich.put_card_by("Herbert", Card.H9)
    stich.put_card_by("Franz", Card.H10)
    assert stich.is_complete()

def test_stich_winner_normal_game_fehl():
    stich = Stich(Vorbehalt.GESUND)
    stich.put_card_by("Peter", Card.HK)
    stich.put_card_by("Günter", Card.H9)
    stich.put_card_by("Herbert", Card.HA)
    stich.put_card_by("Franz", Card.HA)
    assert stich.get_winner() == "Herbert"

def test_stich_winner_normal_game_fehl_abwurf():
    stich = Stich(Vorbehalt.GESUND)
    stich.put_card_by("Peter", Card.HA)
    stich.put_card_by("Günter", Card.H9)
    stich.put_card_by("Herbert", Card.HA)
    stich.put_card_by("Franz", Card.C9)
    assert stich.get_winner() == "Peter"

def test_stich_winner_normal_game_trumpf():
    stich = Stich(Vorbehalt.GESUND)
    stich.put_card_by("Peter", Card.HA)
    stich.put_card_by("Günter", Card.SQ)
    stich.put_card_by("Herbert", Card.H9)
    stich.put_card_by("Franz", Card.H9)
    assert stich.get_winner() == "Günter"

def test_stich_winner_normal_game_trumpf_aufspiel():
    stich = Stich(Vorbehalt.GESUND)
    stich.put_card_by("Peter", Card.D10)
    stich.put_card_by("Günter", Card.CJ)
    stich.put_card_by("Herbert", Card.SQ)
    stich.put_card_by("Franz", Card.D9)
    assert stich.get_winner() == "Herbert"

def test_stich_winner_bubensolo_not_trumpf():
    stich = Stich(Vorbehalt.BUBENSOLO)
    stich.put_card_by("Peter", Card.S10)
    stich.put_card_by("Günter", Card.S9)
    stich.put_card_by("Herbert", Card.SQ)
    stich.put_card_by("Franz", Card.D9)
    assert stich.get_winner() == "Peter"

def test_stich_winner_bubensolo_trumpf():
    stich = Stich(Vorbehalt.BUBENSOLO)
    stich.put_card_by("Peter", Card.S10)
    stich.put_card_by("Günter", Card.CJ)
    stich.put_card_by("Herbert", Card.SQ)
    stich.put_card_by("Franz", Card.D9)
    assert stich.get_winner() == "Günter"
