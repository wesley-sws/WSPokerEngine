class Card:
    # num // 4, % 4 to determine rank and suite (one of diamond, clubs, hearts or spade)
    SUITES = ['C', 'D', 'H', 'S']
    SUITE_TO_LONG_FORM = {'D': "Diamonds", 'C': "Clubs", 'H': "Hearts", 'S': "Spades"}
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    DECK_SIZE = 52
    ALL_CARDS_ID = [i for i in range(DECK_SIZE)]
    def __init__(self, id):
        q, r = divmod(id, 4)
        self.id = id
        self.val = q
        self.rank, self.suite = self.RANKS[q], self.SUITES[r]
    def __str__(self):
        return f"{self.rank} of {self.SUITE_TO_LONG_FORM[self.suite]}"