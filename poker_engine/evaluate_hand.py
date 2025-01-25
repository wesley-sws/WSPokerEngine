import heapq
from collections import defaultdict
from enum import IntEnum
from .players import Player
from .cards import Card

_true_rank_convert = {
    'A': 12, '2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, 
    '8': 6, '9': 7, '10': 8, 'J': 9, 'Q': 10, 'K': 11
}

class HandRank(IntEnum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8

def _check_straight(ranks: list[int]) -> int | None:
    # Pre: ranks is sorted in descending order, len(ranks) >= 5
    for i in range(len(ranks) - 4):  # Need at least 5 cards for a straight
        if ranks[i] - ranks[i+4] == 4:
            return ranks[i+4] + 1
    if ranks[0] == 12 and ranks[-4:] == [3, 2, 1, 0]:
        return 0
    return None

def _get_hand_value(ranks: list[int]) -> int:
    _sum, multiplier = 0, 13
    for i, rank in enumerate(ranks):
        _sum += multiplier ** (len(ranks) - i - 1) * rank
        multiplier -= 1
    return _sum

def _modify_ranks(ranks: list[int], target_len: int, rank_heap: list[int]):
    # modifies the ranks list in-place
    to_exclude = set(ranks)
    while len(ranks) < target_len:
        next_rank = -heapq.heappop(rank_heap)
        if next_rank not in to_exclude:
            ranks.append(next_rank)

def _get_hand_strength(suite_map: dict[str, list[int]], 
                       rank_map: dict[int, int]) -> int:
    flush = flush_ranks = None
    for suite, ranks in suite_map.items():
        if len(ranks) >= 5:
            flush, flush_ranks = suite, sorted(ranks, reverse=True)

    if flush is not None:
        # check straight/royal flush
        if lowest_card := _check_straight(flush_ranks) is not None:
            return (HandRank.STRAIGHT_FLUSH, lowest_card)
    
    count_rank_max = count_rank_max2 = None
    

    rank_heap = []
    for rank, count in rank_map.items():
        if count_rank_max is None or (count, rank) >= count_rank_max:
            count_rank_max, count_rank_max2 = (count, rank), count_rank_max
        elif count_rank_max2 is None or (count, rank) >= count_rank_max2:
            count_rank_max2 = (count, rank)
        rank_heap.append(-rank)
    
    heapq.heapify(rank_heap)

    count1, rank1 = count_rank_max

    if count1 == 4:
        ranks = [rank1]
        _modify_ranks(ranks, 2, rank_heap)
        return (HandRank.FOUR_OF_A_KIND, _get_hand_value(ranks))
    
    count2, rank2 = count_rank_max2

    if count1 == 3 and count2 == 2:
        return (HandRank.FULL_HOUSE, 13 * rank1 + rank2)

    if flush is not None:
        return (HandRank.FLUSH, _get_hand_value(flush_ranks[:5]))

    if lowest_card := _check_straight(sorted(rank_map.keys(), reverse=True)) is not None:
        return (HandRank.STRAIGHT, lowest_card)

    if count1 == 3:
        ranks = [rank1]
        _modify_ranks(ranks, 3, rank_heap)
        return (HandRank.THREE_OF_A_KIND, _get_hand_value(ranks))

    if count1 == 2 and count2 == 2:
        ranks = [rank1, rank2]
        _modify_ranks(ranks, 3, rank_heap)
        return (HandRank.TWO_PAIR, _get_hand_value(ranks))

    if count1 == 2:
        ranks = [rank1]
        _modify_ranks(ranks, 4, rank_heap)
        return (HandRank.ONE_PAIR, _get_hand_value(ranks))
    
    return (HandRank.HIGH_CARD, _get_hand_value([-heapq.heappop(rank_heap) for _ in range(5)]))

def get_players_strength(comm_cards: list[Card], players_in: list[Player]
                         ) -> list[tuple[int, tuple[HandRank, int]]]:
    '''
    Hand Rankings (best to worst) and Determining Tie Breaker within the same ranking 
    Royal Flush - always tie
    Straight Flush - determine by highest card only
    Four of a Kind - determine by rank of the 4-card, else kicker (the other)
    Full House - determine by rank of the 3-card, else the 2-card
    Flush - determine by rank of cards lexicographically
    Straight - determine by highest card only
    Three of a Kind - determine by rank of the 3-card then the rest lexicographically 
    Two Pairs - determine by rank of highest pair, then other pair, then the last card
    One Pair - determine by rank of the pair then the rest lexicographically
    High Card - determine by rank of the cards lexicographically
    NOTE - suites do not affect the ranking of hands in Texas Holdem
    '''
    suite_map = defaultdict(set)
    rank_map = defaultdict(int)

    player_strengths: list[int] = []

    for card in comm_cards:
        rank = _true_rank_convert[card.rank]
        suite_map[card.suite].add(rank)
        rank_map[rank] += 1

    for player in players_in:
        card1, card2 = player.hands
        for card in (card1, card2):
            rank = _true_rank_convert[card.rank]
            suite_map[card.suite].add(rank)
            rank_map[rank] += 1
        player_strengths.append(_get_hand_strength(suite_map, rank_map))
        for card in (card1, card2):
            rank = _true_rank_convert[card.rank]
            suite_map[card.suite].remove(rank)
            rank_map[rank] -= 1
            if rank_map[rank] == 0:
                rank_map.pop(rank)
    
    return player_strengths
