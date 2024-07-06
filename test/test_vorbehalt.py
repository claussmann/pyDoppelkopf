from doppelkopf_server.schema import *
from doppelkopf_server.game import *

def test_vorbehalt_priority():
    assert not Vorbehalt.GESUND.has_priority_over(Vorbehalt.GESUND)
    assert Vorbehalt.SCHMEISSEN.has_priority_over(Vorbehalt.GESUND)

def test_game_not_started_before_vorbehalt():
    g = Game("asdfasdf")
    p1 = g.join("Hermann")
    p2 = g.join("Franz")
    p3 = g.join("Tatjana")
    p4 = g.join("Hannelore")
    assert not g.process_card(p1.token, p1.cards[0])

def test_game_can_be_started_after_vorbehalt():
    g = Game("asdfasdf")
    p1 = g.join("Hermann")
    p2 = g.join("Franz")
    p3 = g.join("Tatjana")
    p4 = g.join("Hannelore")
    
    g.process_vorbehalt(p1.token, Vorbehalt.GESUND)
    g.process_vorbehalt(p2.token, Vorbehalt.GESUND)
    g.process_vorbehalt(p3.token, Vorbehalt.GESUND)
    g.process_vorbehalt(p4.token, Vorbehalt.GESUND)

    assert g.get_events(0)[-1].content.state == GameState.ROUND_STARTED
    assert g.process_card(p1.token, p1.cards[0])