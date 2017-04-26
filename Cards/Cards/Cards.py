from enum import IntEnum
import itertools

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

str_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
str_suits = ['s', 'h', 'd', 'c']

class Card:
    def __init__(self, rank, suit):
        self.Rank = rank
        self.Suit = suit

    def __str__(self):
        return str_ranks[self.Rank]+str_suits[self.Suit]


# Generates all the hands of a single range element
# like 22, A2, A2o, A2s
def gen_combos(hand):
    cards1 = [hand[0]+s for s in str_suits]
    cards2 = [hand[1]+s for s in str_suits]
    if hand[0] == hand[1]:
        return [a+b for (a,b) in itertools.combinations(cards1, 2)]
    if len(hand) == 2:
        return [x+y for x in cards1 for y in cards2 if x != y]
    if hand[2] == 'o':
        return [x+y for x in cards1 for y in cards2 if x[1] != y[1]]
    if hand[2] == 's':
        return [x+y for x in cards1 for y in cards2 if x[1] == y[1]]

# Generates all the hands of a single range element
# like Axo, Ax, Axs, 22, A2, A2o, A2s
def gen_x_combos(hand):
    result = []
    if hand[0].lower() == 'x':
        if hand[1].lower() != 'x':
            raise Exception("WTF")
        
for hand in ['22', 'A2', 'A4o', 'A5s']:
    print("{0} = {1}".format(hand, gen_combos(hand)))
