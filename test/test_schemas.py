import pytest
from doppelkopf_server.schemas import *

def test_vorbehalt_priority():
    assert not Vorbehalt.GESUND.has_priority_over(Vorbehalt.GESUND)
    assert Vorbehalt.SCHMEISSEN.has_priority_over(Vorbehalt.GESUND)
