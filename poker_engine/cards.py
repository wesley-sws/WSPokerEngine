class Card:
    # num // 4, % 4 to determine rank and suite (one of diamond, clubs, hearts or spade)
    SUITES = ['D', 'C', 'H', 'S']
    SUITE_TO_LONG_FORM = {'D': "Diamonds", 'C': "Clubs", 'H': "Hearts", 'S': "Spades"}
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    def __init__(self, card_val):
        q, r = divmod(card_val, 4)
        self.card_val = card_val
        self.rank, self.suite = self.RANKS[q], self.SUITES[r]
    def __str__(self):
        return f"{self.rank} of {self.SUITE_TO_LONG_FORM[self.suite]}"