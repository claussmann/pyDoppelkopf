from enum import Enum

class Card(Enum):
    # Special
    SCHWEIN = "SCHWEIN"; SUPERSCHWEIN = "SUPERSCHWEIN"
    # Diamonds
    D9 = "D9"; DJ = "DJ"; DQ = "DQ"; DK = "DK"; D10 = "D10"; DA = "DA"
    # Heart
    H9 = "H9"; HJ = "HJ"; HQ = "HQ"; HK = "HK"; H10 = "H10"; HA = "HA"
    # Spades
    S9 = "S9"; SJ = "SJ"; SQ = "SQ"; SK = "SK"; S10 = "S10"; SA = "SA"
    # Clubs
    C9 = "C9"; CJ = "CJ"; CQ = "CQ"; CK = "CK"; C10 = "C10"; CA = "CA"
    # Colors
    DIAMOND = "DIAMOND"; HEART = "HEART"; CLUBS = "CLUBS"; SPADES = "SPADES"

    def is_diamond(self):
        dia = [Card.D9, Card.DK, Card.DJ, Card.DQ, Card.D10, Card.DA]
        return self in dia

    def is_heart(self):
        hearts = [Card.H9, Card.HK, Card.HJ, Card.HQ, Card.H10, Card.HA]
        return self in hearts

    def is_spades(self):
        spades = [Card.S9, Card.SK, Card.SJ, Card.SQ, Card.S10, Card.SA]
        return self in spades

    def is_clubs(self):
        clubs = [Card.C9, Card.CK, Card.CJ, Card.CQ, Card.C10, Card.CA]
        return self in clubs

    def color(self):
        if self.is_diamond():
            return Card.DIAMOND
        if self.is_heart():
            return Card.HEART
        if self.is_clubs():
            return Card.CLUBS
        return Card.SPADES 

    def counting_value(self):
        if self in [Card.DJ, Card.HJ, Card.CJ, Card.SJ]:
            return 2
        if self in [Card.DD, Card.HD, Card.CD, Card.SD]:
            return 3
        if self in [Card.DK, Card.HK, Card.CK, Card.SK]:
            return 4
        if self in [Card.D10, Card.H10, Card.C10, Card.S10]:
            return 10
        if self in [Card.DA, Card.HA, Card.CA, Card.SA]:
            return 11
        return 0

class Vorbehalt(Enum):
    PENDING = "PENDING"
    GESUND = "GESUND"
    SCHMEISSEN = "SCHMEISSEN"
    HIDDEN = "HIDDEN"

    def has_priority_over(self, other):
        priorities = [Vorbehalt.SCHMEISSEN, Vorbehalt.GESUND]
        return priorities.index(self) < priorities.index(other)

class GameState(Enum):
    WAIT_VORBEHALT = "WAIT_VORBEHALT"
    WAIT_PLAYERS = "WAIT_PLAYERS"
    ROUND_STARTED = "ROUND_STARTED"