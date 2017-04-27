from enum import Enum, IntEnum
import itertools
import unittest

STR_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
STR_SUITS = ['s', 'h', 'd', 'c']

class Rank(IntEnum):
    Duece = 0
    Trey = 1
    Four = 2
    Five = 3
    Six = 4
    Seven = 5
    Eight = 6
    Nine = 7
    Ten = 8
    Jack = 9
    Queen = 10
    King = 11
    Ace = 12

class Suit(IntEnum):
    Spades = 0
    Hearts = 1
    Diamonds = 2
    Clubs = 3

MAP_RANKS = {'2' : Rank.Duece,
             '3' : Rank.Trey,
             '4' : Rank.Four,
             '5' : Rank.Five,
             '6' : Rank.Six, 
             '7' : Rank.Seven, 
             '8' : Rank.Eight, 
             '9' : Rank.Nine, 
             'T' : Rank.Ten,
             'J' : Rank.Jack, 
             'Q' : Rank.Queen, 
             'K' : Rank.King, 
             'A' : Rank.Ace}

MAP_SUITS = {'s' : Suit.Spades,
             'h' : Suit.Hearts,
             'd' : Suit.Diamonds,
             'c' : Suit.Clubs}



class Card:
    def __init__(self, rank, suit):
        self.Rank = rank
        self.Suit = suit

    def __str__(self):
        return STR_RANKS[self.Rank]+STR_SUITS[self.Suit]

class InvalidHandTypeError(Exception):
    pass

class HandType(Enum):
    """Type of a hole hand

    AA represents the hand is pair.
    AK represents the hand is all combos of AK etc
    eg. 22 = RangeType.AA, 76s = RangeType.AKs
    """
    AA = 0
    AK = 1
    AKo = 2
    AKs = 3
    AX = 4
    AXo = 5
    AXs = 6
    XX = 7
    AhKh = 8

    def parse_hand_type(hand):
        # regex parsing can generate some invalid combos
        # reject them first XA[so]?
        if hand[0].lower() == 'x' \
            and (len(hand) != 2 or hand[1].lower() != 'x'):
            raise InvalidHandTypeError(hand)
        if len(hand) == 4 \
            and hand[1].lower() not in STR_SUITS \
            and hand[3].lower() not in STR_SUITS:
            raise InvalidHandTypeError(hand)
        if len(hand) == 2: 
            if hand[0].lower() == 'x':
                    return HandType.XX 
            if hand[0].lower() == hand[1].lower():
                return HandType.AA
            if hand[1].lower() == 'x':
                return HandType.AX
            return HandType.AK
        if len(hand) == 3 and hand[2].lower() == 'o': 
            return HandType.AXo \
                    if hand[1].lower() == 'x' \
                    else HandType.AKo
        if len(hand) == 3 and hand[2].lower() == 's': 
            return HandType.AXs \
                    if hand[1].lower() == 'x' \
                    else HandType.AKs
        if len(hand) == 4:
            return HandType.AhKh
        ### Unreachable
        raise AssertionError(hand)

class Hand:
    """Hand represents a hand of type HandType
    """

    def __init__(self, hand):
        self.hand = hand
        self.hand_type = HandType.parse_hand_type(self.hand)
        self.combos = self._gen_combos()


    def _gen_combos(self):
        if self.hand_type == HandType.AA:
            cards1 = [self.hand[0]+s for s in STR_SUITS]
            cards2 = [self.hand[1]+s for s in STR_SUITS]
            return [a+b for (a,b) in itertools.combinations(cards1, 2)]
        if self.hand_type == HandType.AK:
            cards1 = [self.hand[0]+s for s in STR_SUITS]
            cards2 = [self.hand[1]+s for s in STR_SUITS]
            return [x+y for x in cards1 for y in cards2 if x != y]
        if self.hand_type == HandType.AKo:
            cards1 = [self.hand[0]+s for s in STR_SUITS]
            cards2 = [self.hand[1]+s for s in STR_SUITS]
            return [x+y for x in cards1 for y in cards2 if x[1] != y[1]]
        if self.hand_type == HandType.AKs:
            cards1 = [self.hand[0]+s for s in STR_SUITS]
            cards2 = [self.hand[1]+s for s in STR_SUITS]
            return [x+y for x in cards1 for y in cards2 if x[1] == y[1]]
        if self.hand_type == HandType.AX:
            suits = [a+b for (a,b) in itertools.product(STR_SUITS, repeat=2)]
            allXhands = \
                [a for a in STR_RANKS if a.lower() != self.hand[0].lower()]
            return [self.hand[0]+b[0]+a+b[1] for a in allXhands for b in suits]
        if self.hand_type == HandType.AXo:
            suits = [a+b for (a,b) in itertools.permutations(STR_SUITS, 2)]
            allXhands = \
                [a for a in STR_RANKS if a.lower() != self.hand[0].lower()]
            return [self.hand[0]+b[0]+a+b[1] for a in allXhands for b in suits]
        if self.hand_type == HandType.AXs:
            allXhands = \
                [a for a in STR_RANKS if a.lower() != self.hand[0].lower()]
            return [self.hand[0]+b+a+b for a in allXhands for b in STR_SUITS]
        if self.hand_type == HandType.XX:
            suits = [a+b for (a,b) in itertools.product(STR_SUITS, repeat=2)]
            ranks = [a+b for (a,b) in itertools.product(STR_RANKS, repeat=2)]
            return [a[0]+b[0]+a[1]+b[1] for a in ranks for b in suits]
        if self.hand_type == HandType.AhKh:
            return [self.hand]
        raise AssertionError("Unsupported HandType")

class TestHands(unittest.TestCase):
    def _sort_combo_elem(self, elem):
        if MAP_RANKS[elem[2]] > MAP_RANKS[elem[0]] \
            or (MAP_RANKS[elem[2]] == MAP_RANKS[elem[0]] \
                and MAP_SUITS[elem[3]] > MAP_SUITS[elem[1]]):
            return elem[2]+elem[3]+elem[0]+elem[1]
        return elem

    def driver(self, hand_str, expected_hand_type, expected_combos):
        h = Hand(hand_str)
        self.assertEqual(h.hand_type, expected_hand_type)
        print("comparing {0} to {1}".format(h.combos, expected_combos))
        self.assertCountEqual(list(map(self._sort_combo_elem, h.combos)), \
                              list(map(self._sort_combo_elem, expected_combos)))

    def test_AA(self):
        self.driver("22", HandType.AA,
            ["2d2c", "2h2s", "2s2c", "2h2d", "2d2s", "2h2c"])
        self.driver("77", HandType.AA,
            ["7d7c", "7h7s", "7s7c", "7h7d", "7d7s", "7h7c"])
        self.driver("AA", HandType.AA,
            ["AdAc", "AhAs", "AsAc", "AhAd", "AdAs", "AhAc"])

    def test_AK(self):
        self.driver("AK", HandType.AK,
            ["AsKs", "AsKh", "AsKd", "AsKc",
             "AhKs", "AhKh", "AhKd", "AhKc",
             "AdKs", "AdKh", "AdKd", "AdKc",
             "AcKs", "AcKh", "AcKd", "AcKc"])
        
        self.driver("37", HandType.AK,
            ["7s3s", "7s3h", "7s3d", "7s3c",
             "7h3s", "7h3h", "7h3d", "7h3c",
             "7d3s", "7d3h", "7d3d", "7d3c",
             "7c3s", "7c3h", "7c3d", "7c3c"])

    def test_AKo(self):
        self.driver("K3o", HandType.AKo,
            ["3sKh", "3sKd", "3sKc",
             "3hKs", "3hKd", "3hKc",
             "3dKs", "3dKh", "3dKc",
             "3cKs", "3cKh", "3cKd"])
        
        self.driver("27o", HandType.AKo,
            ["7s2h", "7s2d", "7s2c",
             "7h2s", "7h2d", "7h2c",
             "7d2s", "7d2h", "7d2c",
             "7c2s", "7c2h", "7c2d"])

    def test_AKs(self):
        self.driver("Q2s", HandType.AKs,
             ["Qs2s", "Qh2h", "Qd2d", "Qc2c"])
        
        self.driver("49s", HandType.AKs,
             ["4s9s", "4h9h", "4d9d", "4c9c"])

    def test_AX(self):
        expected_result = []
        for rank in STR_RANKS:
            if rank != '9':
                expected_result = expected_result+ Hand(rank+'9').combos
        self.driver("9x", HandType.AX, expected_result)

    def test_AXo(self):
        expected_result = []
        for rank in STR_RANKS:
            if rank != 'Q':
                expected_result = expected_result+ Hand(rank+'Qo').combos
        self.driver("Qxo", HandType.AXo, expected_result)

    def test_AXs(self):
        expected_result = []
        for rank in STR_RANKS:
            if rank != 'K':
                expected_result = expected_result+ Hand(rank+'Ks').combos
        self.driver("Kxs", HandType.AXs, expected_result)

    def test_XX(self):
        #TODO
        pass

if __name__ == "__main__":
    unittest.main()