import pytest
from doppelkopf_server.runde import *
from doppelkopf_server.schemas import *

def test_card_shuffle():
    runde = Runde("Albert", "Bernd", "Fred", "Anne")
    albert = runde.get_hand("Albert")
    bernd = runde.get_hand("Bernd")
    fred = runde.get_hand("Fred")
    anne = runde.get_hand("Anne")
    all_cards = albert + bernd + fred + anne

    assert len([c for c in all_cards if c == Card.D10]) == 2
    assert len([c for c in all_cards if c == Card.CK]) == 2
    assert len([c for c in all_cards if c == Card.SA]) == 2
    assert len(albert) == 12
    assert len(bernd) == 12
    assert len(fred) == 12
    assert len(anne) == 12

def test_runde_removes_card_after_putting_it():
    runde = Runde("Albert", "Bernd", "Fred", "Anne")
    runde.put_vorbehalt("Albert", Vorbehalt.GESUND)
    runde.put_vorbehalt("Bernd", Vorbehalt.GESUND)
    runde.put_vorbehalt("Fred", Vorbehalt.GESUND)
    runde.put_vorbehalt("Anne", Vorbehalt.GESUND)
    albert = list(runde.get_hand("Albert"))
    card = albert[0]
    runde.put_card("Albert", card)

    albert.remove(card)
    assert runde.get_hand("Albert") == albert

def test_runde_player_sequence():
    runde = Runde("Albert", "Bernd", "Fred", "Anne")
    runde.put_vorbehalt("Albert", Vorbehalt.GESUND)
    runde.put_vorbehalt("Bernd", Vorbehalt.GESUND)
    runde.put_vorbehalt("Fred", Vorbehalt.GESUND)
    runde.put_vorbehalt("Anne", Vorbehalt.GESUND)
    albert = list(runde.get_hand("Albert"))
    bernd = list(runde.get_hand("Bernd"))

    assert not runde.put_card("Bernd", bernd[0])
    assert bernd == runde.get_hand("Bernd")
    assert runde.put_card("Albert", albert[0])
    assert runde.put_card("Bernd", bernd[0])
