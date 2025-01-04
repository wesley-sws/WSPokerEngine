from random import randint
from collections import defaultdict
from enum import IntEnum
import heapq
# num // 4, % 4 to determine rank and suite (one of diamond, clubs, hearts or spade)
# Raise Rule - The minimum raise must be at least equal to the size of the previous raise

suites = ['D', 'C', 'H', 'S']
suite_to_long_form = {'D': "Diamonds", 'C': "Clubs", 'H': "Hearts", 'S': "Spades"}
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
true_rank_convert = {
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

class Card:
    def __init__(self, card_num):
        q, r = divmod(card_num, 4)
        self.rank, self.suite = ranks[q], suites[r]
    def __str__(self):
        return f"{self.rank} of {suite_to_long_form[self.suite]}"

class Player:
    def __init__(self, id: int, balance: int, money_in: int, hands: tuple[Card]):
        self.id = id
        self.hands = hands
        self.balance = balance
        self.money_in = money_in
        self.folded = False
        self.gone_max = False
    
    def get_player_status(self, include_hand: bool) -> str:
        res = [
            f"Player {self.id}: Your balance is {self.balance}, ",
            f"have spent {self.money_in} in this game and have ",
            f'{"" if self.folded else "not yet "}' + "folded."
        ]
        if include_hand:
            res.append(f"\nYour hands are {self.hands[0]}, and {self.hands[1]}")
        return ''.join(res)

class TexasHoldem:
    class HandSession:
        def __init__(
            self, players_info: list[int], 
            small_blind_player_i: int, blinds: list[int], game_num
        ):
            self.game_num = game_num
            self.player_num = len(players_info)
            self.num_players_gone_max = self.num_players_folded = 0
            # initialise cards
            all_cards: set[int] = set()
            while len(all_cards) < 5 + 2 * self.player_num:
                all_cards.add(randint(0, 13 * 4 - 1))
            all_cards_list = list(all_cards)
            # initialise players
            self.players: Player = [
                Player(id, balance, 0, 
                    (
                        Card(all_cards_list.pop()),
                        Card(all_cards_list.pop())
                    )
                )
                for id, balance in players_info
            ]
            self.comm_cards: list[Card] = [Card(card) for card in all_cards_list]
            self.curr_bet = self.round_num = 0
            self.start_player_i = self.setup_blinds(small_blind_player_i, blinds)
            self.round_to_comm_cards = [0, 3, 4, 5]
            # now find the players of highest and second highest balance (use case 
            # can be seen later in the round function)
            self.balance_heap = [-balance for _, balance in players_info]
            heapq.heapify(self.balance_heap)
            self.highest_balance = -heapq.heappop(self.balance_heap)
            self.snd_highest_balance = -heapq.heappop(self.balance_heap)
        
        def setup_blinds(self, small_blind_i, blinds: list[int]) -> int:
            for blind_index, player_id in enumerate((
                small_blind_i, 
                (small_blind_i + 1) % self.player_num # big blind index
            )):
                player: Player = self.players[player_id]
                blind_actual = blinds[blind_index]
                if player.balance < blind_actual:
                    blind_actual = player.balance
                    player.gone_max = True
                player.money_in += blind_actual
                player.balance -= blind_actual
                if blind_index == 1: # big blind
                    self.curr_bet = blind_actual
            return (small_blind_i + 2) % self.player_num
        
        def get_status(self):
            res = [
                f"We are at round {self.round_num} of game {self.game_num}\n",
                "The community cards "
            ]
            res.append("have not been revealed" if self.round_num == 0 
                else f"are {', '.join(map(
                        str, self.comm_cards[:self.round_to_comm_cards[self.round_num]]
                    ))}")
            res.append(
                '\n' + '\n'.join(player.get_player_status(False) 
                for player in self.players)
            )
            return ''.join(res)

        def round(self):
            print(self.get_status())
            # to bypass the initial condition to enter for loop at first occurence
            ending_player_i = None
            curr_player_i = self.start_player_i
            last_full_raise = self.curr_bet

            while ending_player_i is None or curr_player_i != ending_player_i:
                if ending_player_i is None:
                    ending_player_i = curr_player_i
                player: Player = self.players[curr_player_i]
                initial_balance = player.balance
                # F for fold, C for Check, A for All in, R,<N> to raise by N
                if not player.folded and not player.gone_max:
                    print(player.get_player_status(True))
                    '''
                    Let us consider cases when all in, check, and raise should not be a player's option
                    Check
                    - player doesn't have enough to check so can only go all in
                    All in 
                    - player is the sole wealthiest player (so can only raise up to the next wealthiest person instead)
                    RAISE
                    - player doesn't have enough to raise an adequate amount
                    - player is the sole wealthiest player and second wealthiest player has gone all in, so can't raise nor go all in
                    More cases for RAISE:
                    - player is the richest person and the remaining balance of the next 
                        richest player is less than the last full raise, hence player can raise by the 
                        amount that the next richest player has left
                    '''
                    # corner case handled implicitly:
                    # if remaining to call is negative (small blinds > big blinds)
                    print(f"The current bet is {self.curr_bet}")
                    only_richest = self.highest_balance == player.balance + player.money_in \
                        and self.highest_balance != self.snd_highest_balance
                    options: list[str] = ["Fold (enter F)"]
                    if not only_richest:
                        options.append("All in (enter A)")

                    remaining_to_call = self.curr_bet - player.money_in
                    if player.balance > remaining_to_call: # exclusive as if equal only allow all-in
                        options.append(f"Check at {self.curr_bet} (enter C)")
                        if last_full_raise + remaining_to_call < player.balance and not only_richest or \
                            only_richest and self.curr_bet < self.snd_highest_balance:
                            raise_min, raise_max = last_full_raise, player.balance - remaining_to_call
                            if only_richest:
                                raise_min = min(last_full_raise, self.snd_highest_balance - self.curr_bet)
                                raise_max = self.snd_highest_balance - self.curr_bet
                            options.append(
                                f"Raise by minimum {raise_min}, maximum {raise_max}"
                                " (enter R,<N> with N being raise amount)"
                            )
                    user_input = input(
                        f"Would you like to {', '.join(options[:-1])}"
                        f"{", or " if len(options) > 1 else ""}"
                        f"{options[-1]}?\n"
                    )
                    commands = set(map(lambda x:x[0], options))
                    if user_input[0] not in commands:
                        raise ValueError
                    elif user_input == 'F':
                        player.folded = True
                        self.num_players_folded += 1
                        if self.num_players_folded == self.player_num - 1:
                            break
                        # note heap won't be empty since otherwise that means there is only 1 player 
                        # that has yet to fold, which has been considered with the 'break' above
                        player_total = player.balance + player.money_in
                        if player_total == self.highest_balance:
                            self.highest_balance = self.snd_highest_balance
                        if player_total >= self.snd_highest_balance: # player is highest or 2nd highest
                            self.snd_highest_balance = -heapq.heappop(self.balance_heap)
                    elif user_input == 'A':
                        player.money_in += player.balance
                        if player.money_in > self.curr_bet:
                            self.curr_bet = player.money_in
                            ending_player_i = curr_player_i
                        last_full_raise = max(last_full_raise, player.balance)
                        player.balance = 0
                        player.gone_max = True
                        self.num_players_gone_max += 1
                    elif user_input == 'C':
                        player.balance -= remaining_to_call
                        player.money_in += remaining_to_call
                        assert player.money_in == self.curr_bet
                        if self.curr_bet == self.snd_highest_balance:
                            player.gone_max = True
                            self.num_players_gone_max += 1
                    else:
                        new_raised = int(user_input[2:])
                        if raise_min > new_raised or new_raised > raise_max:
                            raise ValueError
                        '''
                        note if new_raised < last_full_raise, this could only mean 
                        the current player is the only richest player and he's raising to the second richest
                        so everyone has to go all in regardless of what last_full_raise is 
                        '''
                        last_full_raise = new_raised
                        new_in = new_raised + remaining_to_call
                        player.balance -= new_in
                        player.money_in += new_in
                        self.curr_bet = self.curr_bet + new_raised
                        if only_richest and new_raised + self.curr_bet == self.snd_highest_balance \
                            or player.balance == 0:
                            player.gone_max = True
                            self.num_players_gone_max += 1
                        ending_player_i = curr_player_i
                    print(
                        f"You have put {initial_balance - player.balance} in this round. "
                        f"Your new balance is {player.balance}"
                    )
                curr_player_i = (curr_player_i + 1) % self.player_num
            self.round_num += 1
            self.start_player_i = (self.start_player_i + 1) % self.player_num

        def check_straight(self, ranks: list[int]) -> int | None:
            # Pre: ranks is sorted in descending order, len(ranks) >= 5
            for i in range(len(ranks) - 4):  # Need at least 5 cards for a straight
                if ranks[i] - ranks[i+4] == 4:
                    return ranks[i+4] + 1
            if ranks[0] == 12 and ranks[-4:] == [3, 2, 1, 0]:
                return 0
            return None
        
        def get_hand_value(self, ranks: list[int]) -> int:
            _sum, multiplier = 0, 13
            for i, rank in enumerate(ranks):
                _sum += multiplier ** (len(ranks) - i - 1) * rank
                multiplier -= 1
            return _sum
        
        def modify_ranks(self, ranks: list[int], target_len: int, rank_heap: list[int]):
            # modifies the ranks list in-place
            to_exclude = set(ranks)
            while len(ranks) < target_len:
                next_rank = -heapq.heappop(rank_heap)
                if next_rank not in to_exclude:
                    ranks.append(next_rank)
        
        def get_hand_strength(self, suite_map: dict[str, list[int]], rank_map: dict[int, int]) -> int:
            flush = flush_ranks = None
            for suite, ranks in suite_map.items():
                if len(ranks) >= 5:
                    flush, flush_ranks = suite, sorted(ranks, reverse=True)

            if flush is not None:
                # check straight/royal flush
                if lowest_card := self.check_straight(flush_ranks) is not None:
                    return (HandRank.STRAIGHT_FLUSH, lowest_card)
            
            rank_count_heap, rank_heap = [], []
            for rank, count in rank_map.items():
                rank_count_heap.append((-count, -rank))
                rank_heap.append(-rank)
            heapq.heapify(rank_count_heap)
            heapq.heapify(rank_heap)

            count1, rank1 = heapq.heappop(rank_count_heap)
            count1, rank1 = -count1, -rank1

            if count1 == 4:
                ranks = [rank1]
                self.modify_ranks(ranks, 2, rank_heap)
                return (HandRank.FOUR_OF_A_KIND, self.get_hand_value(ranks))
            
            count2, rank2 = heapq.heappop(rank_count_heap)
            count2, rank2 = -count2, -rank2

            if count1 == 3 and count2 == 2:
                return (HandRank.FULL_HOUSE, 13 * rank1 + rank2)

            if flush is not None:
                return (HandRank.FLUSH, self.get_hand_value(flush_ranks[:5]))

            if lowest_card := self.check_straight(sorted(rank_map.keys(), reverse=True)) is not None:
                return (HandRank.STRAIGHT, lowest_card)

            if count1 == 3:
                ranks = [rank1]
                self.modify_ranks(ranks, 3, rank_heap)
                return (HandRank.THREE_OF_A_KIND, self.get_hand_value(ranks))

            if count1 == 2 and count2 == 2:
                ranks = [rank1, rank2]
                self.modify_ranks(ranks, 3, rank_heap)
                return (HandRank.TWO_PAIR, self.get_hand_value(ranks))

            if count1 == 2:
                ranks = [rank1]
                self.modify_ranks(ranks, 4, rank_heap)
                return (HandRank.ONE_PAIR, self.get_hand_value(ranks))
            
            return (HandRank.HIGH_CARD, self.get_hand_value([-heapq.heappop(rank_heap) for _ in range(5)]))

        def get_players_strength(self, players_in: list[Player]) -> list[tuple[int, tuple[HandRank, int]]]:
            '''
            Hand Rankings (best to worst) and Determining Tie Breaker within the same ranking 
            Royal Flush - always tie
            Straight Flush - determine by highest card only
            Four of a Kind - determine by rank of the 4-card, else kicker (the other)
            Full House - determine by rank of the 3-card, else the 2-card
            Flush - determine by rank of 
            Straight - determine by highest card only
            Three of a Kind - determine by rank of the 3-card then the rest lexicographically 
            Two Pairs - determine by rank of highest pair, then other pair, then the rest lexicographically
            One Pair - determine by rank of the pair then the rest lexicographically
            High Card - determine by rank of the cards lexicographically
            NOTE - suites do not affect the ranking of hands in Texas Holdem
            '''
            suite_map = defaultdict(set)
            rank_map = defaultdict(int)

            player_strengths: list[int] = []

            for card in self.comm_cards:
                rank = true_rank_convert[card.rank]
                suite_map[card.suite].add(rank)
                rank_map[rank] += 1

            for player in players_in:
                card1, card2 = player.hands
                for card in (card1, card2):
                    rank = true_rank_convert[card.rank]
                    suite_map[card.suite].add(rank)
                    rank_map[rank] += 1
                player_strengths.append(self.get_hand_strength(suite_map, rank_map))
                for card in (card1, card2):
                    rank = true_rank_convert[card.rank]
                    suite_map[card.suite].remove(rank)
                    rank_map[rank] -= 1
                    if rank_map[rank] == 0:
                        rank_map.pop(rank)
            
            return player_strengths

        def pot_distribution(self, players_in: list[Player], player_hand_strength: list[int]):
            assert len(players_in) == len(player_hand_strength)
            winner_rank: list[tuple[tuple[HandRank, int], set[int]]] = []
            for i in range(len(players_in)):
                id, strength = players_in[i].id, player_hand_strength[i]
                print(f"Player {id} has stength {strength}")
                while winner_rank and winner_rank[-1][0] < strength:
                    winner_rank.pop()
                if not winner_rank or strength < winner_rank[-1][0]:
                    winner_rank.append((strength, {id}))
                else: # strength == winner_rank[-1][0]
                    winner_rank[-1][1].add(id)

            # initialise and begin pot distribution
            winners_i, winners = 0, winner_rank[0][1]
            player_num = len(players_in)
            winner_cumm = money_checked = pot_count = 0
            for i, player in enumerate(players_in):
                if player.id in winners:
                    winner_cumm += (player.money_in - money_checked) * (player_num - i) / len(winners)
                    if winner_cumm > 0:
                        player.balance += winner_cumm
                        print(
                            f"Player {player.id} has won "
                            f"{'Main Pot' if pot_count == 0 else f'Side Pot {pot_count}'}"
                            f"! Your current balance is now {player.balance}"
                        )
                    money_checked = player.money_in
                    winners.remove(i)
                    if len(winners) == 0:
                        winners_i += 1
                        pot_count += 1
                        if winners_i == len(winner_rank):
                            break
                        winners = winner_rank[winners_i][1]
                        winner_cumm = 0
                else:
                    winner_cumm += (player.money_in - money_checked) / len(winners)

        def showdown(self, players_in: list[Player]):
            assert len(players_in) > 0
            print(self.get_status())
            players_in.sort(key=lambda player: player.money_in)
            player_hand_strength: list[int] = self.get_players_strength(players_in)
            self.pot_distribution(players_in, player_hand_strength)

        def play(self) -> list[int]:
            for _ in range(4):
                self.round()
                if self.num_players_folded == self.player_num - 1:
                    winner: Player = next(player for player in self.players if not player.folded)
                    total_in = sum(map(lambda player: player.money_in, self.players))
                    winner.balance += total_in
                    print(
                        f"Player {winner.id} won an {total_in}!"
                        "Your new balance is " + str(winner.balance)
                    )
                    return
                elif self.num_players_folded + self.num_players_gone_max == self.player_num:
                    break
            print("TIME FOR SHOWDOWN!!!")
            self.round_num = 3
            self.showdown([player for player in self.players if not player.folded])
            print("FINAL BALANCE")
            print('\n'.join((f"Player {i} has {player.balance}") for i, player in enumerate(self.players)))
            return [player.balance for player in self.players]

    def __init__(self, players: int, blinds : list[int],
                 player_balance: list[int],
                 player_ids: list[int] | None = None,
                 small_blind_i: int = 0):
        assert len(player_balance) > 1
        assert len(blinds) == 2
        assert 5 + players * 2 <= 52
        player_ids = player_ids or list(range(len(player_balance)))
        self.players_info = list(zip(player_ids, player_balance))
        self.small_blind_player_i = small_blind_i
        self.blinds = blinds
        self.game_num = 0
    
    def _run_session(self) -> bool:
        print(self.players_info)
        newSession = self.HandSession(
            self.players_info,
            self.small_blind_player_i, self.blinds, self.game_num
        )
        updated_balance = newSession.play()
        new_players_info = []
        next_small_blind = None
        for i, balance in enumerate(updated_balance):
            if balance != 0:
                if next_small_blind is None and i > self.small_blind_player_i:
                    next_small_blind = len(new_players_info)
                new_players_info.append((self.players_info[i][0], balance))
        self.game_num += 1
        if len(new_players_info) == 1:
            id, balance = new_players_info[0]
            print(
                f"WE HAVE A WINNER! Player {id} is the only one left with a "
                f"balance of {balance}. Congrats!"
            )
            return True
        self.small_blind_player_i = 0 if next_small_blind is None else next_small_blind
        self.players_info = new_players_info
        return False


    def play(self, round_limit=None):
        if round_limit is None:
            while input("Would you like to start a new round (Y for yes, anything else for no)?\n") == 'Y':
                if self._run_session():
                    break
        else:
            for _ in range(round_limit):
                if self._run_session():
                    break

# example
TexasHoldem(5, [5, 10], [200, 300, 400, 500, 600]).play()
