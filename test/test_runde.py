import pytest
from doppelkopf_server.runde import *
from doppelkopf_server.schemas import *

def test_card_shuffle():
    runde = Runde("Albert", "Bernd", "Fred", "Anne", 0)
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
