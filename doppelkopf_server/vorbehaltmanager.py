import time
from doppelkopf_server.schemas import *

class VorbehaltManager:
    def __init__(self):
        self.vorbehalte = list()

    def new_vorbehalt(self, player: str, vorbehalt: Vorbehalt):
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
        return (winner, vorbehalt)
