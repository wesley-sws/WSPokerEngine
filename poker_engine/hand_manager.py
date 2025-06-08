from random import randint
from collections.abc import Iterable, Generator
import heapq
from .cards import Card
from .players import Player
from . import evaluate_hand

class HandManager:
    _round_to_comm_cards = [0, 3, 4, 5]
    # Raise Rule - The minimum raise must be at least equal to the size of the previous raise IN THE SAME BETTING ROUND
    # The current implementation is for the TexasHoldem Variant, but more to be potentially implemented
    def __init__(
        self, players_info: list[int], 
        small_blind_player_i: int, blinds: list[int]
    ):
        self._player_num = len(players_info)
        self._num_players_gone_max = self._num_players_folded = 0
        # initialise cards
        all_cards: set[int] = set()
        while len(all_cards) < 5 + 2 * self._player_num:
            all_cards.add(randint(0, 13 * 4 - 1))
        all_cards_list = list(all_cards)
        # initialise players
        self._players: list[Player] = [
            Player(id, balance, 0, 
                (
                    Card(all_cards_list.pop()),
                    Card(all_cards_list.pop())
                )
            )
            for id, balance in players_info
        ]
        self._comm_cards: list[Card] = [Card(card) for card in all_cards_list]
        self._curr_bet = self._round_num = 0
        self._start_player_i = self._setup_blinds(small_blind_player_i, blinds)
        # now find the players of highest and second highest balance (use case 
        # can be seen later in the betting_round function)
        self._balance_heap = [-balance for _, balance in players_info]
        heapq.heapify(self._balance_heap)
        self._highest_balance = -heapq.heappop(self._balance_heap)
        self._snd_highest_balance = -heapq.heappop(self._balance_heap)
        self._small_blind_player = small_blind_player_i
        self.big_blind = blinds[1]
        self._winners = []
    
    def _setup_blinds(self, small_blind_i: int, blinds: list[int]) -> int:
        for blind_index, player_id in enumerate((
            small_blind_i, 
            (small_blind_i + 1) % self._player_num # big blind index
        )):
            player: Player = self._players[player_id]
            blind_actual = blinds[blind_index]
            if player.balance < blind_actual:
                blind_actual = player.balance
                player.gone_max = True
            player.money_in += blind_actual
            player.balance -= blind_actual
            if blind_index == 1: # big blind
                self._curr_bet = blind_actual
        return (small_blind_i + 2) % self._player_num
    
    @property
    def status(self):
        return {
            "round_num": self._round_num,
            "revealed_comm_cards": self._comm_cards[:self._round_to_comm_cards[min(3, self._round_num)]],
            "players_status": [player.status for player in self._players]
        }
    
    def _get_available_options(self, curr_player: Player, last_full_raise: int, 
                                remaining_to_call: int, only_richest: bool
                                ) -> dict:
        '''
        Let us consider cases when all in, check, and raise should not be a player's option
        Check
        - player doesn't have enough to check so can only go all in
        All in 
        - player is the sole wealthiest player 
        (essentially going all in is equivalent raising up to the next wealthiest person, 
        so we just don't show the all in option for clearer UI)
        RAISE
        - player doesn't have enough to raise the minimum amount required
        - player is the sole wealthiest player and second wealthiest player has gone all in, so can't raise nor go all in
        More cases for RAISE:
        - player is the richest person and the remaining balance of the next 
        richest player is less than the last full raise, hence player can raise by the 
        amount that the next richest player has left
        corner case handled implcitly: if remaining to call is negative (small blinds > big blinds)
        '''
        options = {
            "F": True, "A": False, "C": False, "R": None
        }
        if not only_richest:
            options["A"] = True
        if curr_player.balance > remaining_to_call: # exclusive as if equal only allow all-in
            options["C"] = True
            if last_full_raise + remaining_to_call < curr_player.balance and not only_richest or \
                only_richest and self._curr_bet < self._snd_highest_balance:
                raise_min, raise_max = last_full_raise, curr_player.balance - remaining_to_call
                if only_richest:
                    raise_min = min(last_full_raise, self._snd_highest_balance - self._curr_bet)
                    raise_max = self._snd_highest_balance - self._curr_bet
                options["R"] = (raise_min, raise_max)
        
        return options

    def _handle_user_option(self, options: dict, user_option: dict, 
            player: Player, last_full_raise: int, remaining_to_call: int, 
            only_richest: bool) -> tuple[bool, int, bool]:
        # return last_full_raise and whether player has raised to be updated
        if user_option["action"] not in options or not options[user_option["action"]]:
            raise ValueError
        
        player_raised = False
        if user_option["action"] == 'F':
            player.folded = True
            self._num_players_folded += 1
            if self._num_players_folded == self._player_num - 1:
                return player_raised, last_full_raise, True
            # note heap won't be empty since otherwise that means there is only 1 player 
            # that has yet to fold, which has been considered with the 'break' above
            player_total = player.balance + player.money_in
            if player_total == self._highest_balance:
                self._highest_balance = self._snd_highest_balance
            if player_total >= self._snd_highest_balance: # player is highest or 2nd highest
                self._snd_highest_balance = -heapq.heappop(self._balance_heap)
        elif user_option["action"] == 'A':
            player.money_in += player.balance
            if player.money_in > self._curr_bet:
                self._curr_bet = player.money_in
                player_raised = True
            last_full_raise = max(last_full_raise, player.balance)
            player.balance = 0
            player.gone_max = True
            self._num_players_gone_max += 1
        elif user_option["action"] == 'C':
            player.balance -= remaining_to_call
            player.money_in += remaining_to_call
            assert player.money_in == self._curr_bet
            if self._curr_bet == self._snd_highest_balance:
                player.gone_max = True
                self._num_players_gone_max += 1
        else:
            new_raised = user_option["amount"]
            raise_min, raise_max = options["R"]
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
            self._curr_bet = self._curr_bet + new_raised
            if only_richest and new_raised + self._curr_bet == self._snd_highest_balance \
                or player.balance == 0:
                player.gone_max = True
                self._num_players_gone_max += 1
            player_raised = True
        return player_raised, last_full_raise, False


    def betting_round(self) -> Generator[dict, dict, dict]:
        '''
        NOTE: There seems to be a bug at the moment on round concerning folding
        and going all in, more to be done on this, can test just by 
        playing a game where you keep going all in / check / fold
        '''
        if self._round_num > 3:
            raise ValueError("Game has ended")
        # to bypass the initial condition to enter for loop at first occurence
        ending_player_i = None
        curr_player_i = self._start_player_i
        last_full_raise = self.big_blind
        last_action_result = None
        while ending_player_i is None or curr_player_i != ending_player_i:
            if ending_player_i is None:
                ending_player_i = curr_player_i
            player: Player = self._players[curr_player_i]
            initial_balance = player.balance
            # F for fold, C for Check, A for All in, R,<N> to raise by N
            if not player.folded and not player.gone_max:
                only_richest = self._highest_balance == player.balance + player.money_in \
                    and self._highest_balance != self._snd_highest_balance
                remaining_to_call = self._curr_bet - player.money_in
                options = self._get_available_options(
                    player, last_full_raise, remaining_to_call, only_richest
                )
                '''
                Expected user_option format:
                {
                "action": str # one of "F", "A", "C", "R">,
                "amount": int # required if action is "R" (ignore otherwise)
                }
                '''
                user_option = yield {
                    "player_status": player.status,
                    "current_bet": self._curr_bet,
                    "options": options,
                    "last_action_result": last_action_result # None at first yield
                }
                
                player_raised, last_full_raise, to_break = self._handle_user_option(
                    options, user_option, player, last_full_raise, 
                    remaining_to_call, only_richest
                )
                if player_raised:
                    ending_player_i = curr_player_i

                last_action_result = {
                    "id": player.id,
                    "last_put": initial_balance - player.balance,
                    "new_balance": player.balance
                }
                if to_break:
                    break
            curr_player_i = (curr_player_i + 1) % self._player_num
        self._start_player_i = self._small_blind_player
        self._round_num += 1
        return last_action_result

    def _pot_distribution(self, players_in: list[Player], 
                          players_hand_strength: 
                            list[tuple[evaluate_hand.HandRank, int]]
                          ) -> Generator[dict, None, None]:
        # yields winners
        assert len(players_in) == len(players_hand_strength)
        winner_rank = []
        for i in range(len(players_in)):
            id, strength = players_in[i].id, players_hand_strength[i]
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
                    player.balance += int(winner_cumm)
                    yield {
                        "id": player.id,
                        "pot_count": pot_count, # 0 for main pot
                        "new_balance": player.balance,
                        "hand_strength": players_hand_strength[i][0]
                    }
                money_checked = player.money_in
                winners.remove(player.id)
                if len(winners) == 0:
                    winners_i += 1
                    pot_count += 1
                    if winners_i == len(winner_rank):
                        break
                    winners = winner_rank[winners_i][1]
                    winner_cumm = 0
            else:
                winner_cumm += (player.money_in - money_checked) / len(winners)
            
    def _showdown(self) -> Generator[dict, None, None]:
        players_in = [player for player in self._players if not player.folded]
        assert len(players_in) > 0
        players_in.sort(key=lambda player: player.money_in)
        players_hand_strength: list[tuple[evaluate_hand.HandRank, int]] = \
          evaluate_hand.get_players_strength(
            self._comm_cards, players_in
        )
        return self._pot_distribution(players_in, players_hand_strength)

    def is_complete(self) -> bool:
        """
        Checks if the game has ended and performs game-finalizing logic.
        Returns True if the game is over, False otherwise.
        """
        if self._round_num > 4:
            return True
        
        if self._num_players_folded == self._player_num - 1:
            self._round_num = 5 # game ends
            winner: Player = next(player for player in self._players if not player.folded)
            ''' TODO
            Can improve complexity by having total_pot as a field and adding to
            it at _handle_user_option instead of summing it here
            '''
            total_in = sum(player.money_in for player in self._players)
            winner.balance += total_in
            self._winners = ({
                "id": winner.id,
                "pot_count": 0, # 0 for main pot
                "new_balance": winner.balance,
                "hand_strength": None
            },) 
        elif self._num_players_folded + self._num_players_gone_max >= self._player_num - 1 or self._round_num == 4:
            self._round_num = 5
            self._winners = self._showdown()
        else:
            return False
        return True

    @property
    def winners(self) -> Iterable[dict]:
        if not self._winners:
            raise ValueError("Game has not ended yet")
        return self._winners

    @property
    def players_balance(self) -> list[int]:
        return [player.balance for player in self._players]
