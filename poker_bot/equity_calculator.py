'''
Run from root PYTHONPATH=. python poker_bot/equity_calculator.py
'''
from phevaluator import evaluate_cards
from poker_engine.cards import Card
from typing import Optional
import random
class EquityCalculator:
    def _evaluate_hand_strength(self, cards: tuple[Card, Card], players: int, 
                                board: Optional[list[Card]] = None, iterations=10000) -> float:
        '''
        Calculates equity using monte carlo
        Use external library for evaluate_cards for speed purposes (as need to run many iterations)
        '''
        assert len(cards) == 2
        assert not board or 3 <= len(board) <= 5
        card1, card2 = cards
        used_cards: set[int] = {card1.id, card2.id}
        board_used: list[int] = [] if not board else [card.id for card in board]
        wins = 0
        if len(board_used) == 5: 
            # evaluate player hand outside of loop if board complete
            used_cards.update(board_used)
            player_hand_rank = evaluate_cards(card1.id, card2.id, *board_used)
        unused_cards: list[int] = list(filter(lambda x: x not in used_cards, Card.ALL_CARDS_ID))
        new_cards_per_it: int = 5 - len(board_used) + (players - 1) * 2
        for _ in range(iterations):
            new_cards: list[int] = random.sample(unused_cards, new_cards_per_it)
            new_comm_cards = []
            if len(board_used) != 5:
                new_comm_cards = new_cards[len(board_used)-5:]
                player_hand_rank = evaluate_cards(card1.id, card2.id, *board_used, *new_comm_cards)
            if all(
                evaluate_cards(
                    new_cards[2*i], new_cards[2*i+1], *board_used, *new_comm_cards
                ) > player_hand_rank for i in range(players - 1)
                    ):
                wins += 1
        return wins / iterations

