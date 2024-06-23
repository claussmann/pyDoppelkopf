import pytest
from doppelkopf_server.schemas import *
from doppelkopf_server.runde import *

def test_vorbehalt_manager():
    v = VorbehaltManager()
    v.new_vorbehalt("Heinz", Vorbehalt.GESUND)
    v.new_vorbehalt("Erwin", Vorbehalt.GESUND)
    assert not v.is_ready()
    v.new_vorbehalt("Hermann", Vorbehalt.ARMUT)
    v.new_vorbehalt("Eddi", Vorbehalt.GESUND)
    assert v.is_ready()
    assert v.evaluate() == ("Hermann", Vorbehalt.ARMUT)

def test_vorbehalt_manager_player_dublicate():
    v = VorbehaltManager()
    v.new_vorbehalt("Heinz", Vorbehalt.GESUND)
    v.new_vorbehalt("Erwin", Vorbehalt.GESUND)
    v.new_vorbehalt("Hermann", Vorbehalt.ARMUT)
    v.new_vorbehalt("Hermann", Vorbehalt.GESUND)
    assert not v.is_ready()
    v.new_vorbehalt("Eddi", Vorbehalt.GESUND)
    assert v.is_ready()
    assert v.evaluate() == ("Hermann", Vorbehalt.ARMUT)
