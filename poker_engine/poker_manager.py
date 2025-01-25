from .hand_manager import HandManager
from collections.abc import Callable, Generator

class PokerManager:
    def __init__(self, blinds : list[int],
                 player_balance: list[int],
                 player_ids: list[int] | None = None,
                 small_blind_i: int = 0):
        assert len(player_balance) > 1
        assert len(blinds) == 2
        assert 5 + len(player_balance) * 2 <= 52
        player_ids = player_ids or list(range(len(player_balance)))
        self._players_info = list(zip(player_ids, player_balance))
        self.small_blind_player_i = small_blind_i
        self.blinds = blinds
        self._game_num = 0
    
    @property
    def status(self) -> dict:
        return {
            "players_info": self._players_info,
            "small_blind_player_i": self.small_blind_player_i,
            "blinds": self.blinds,
            "game_num": self._game_num
        }
    
    def advance(self) -> Generator[HandManager, None, None]:
        while len(self._players_info) > 1:
            new_hand = HandManager(
                self._players_info,
                self.small_blind_player_i, self.blinds
            )
            yield new_hand
            self.update_player_info(new_hand.players_balance)

    def update_player_info(self, updated_balance: int):
        new_players_info = []
        next_small_blind = None
        for i, balance in enumerate(updated_balance):
            if balance != 0:
                if next_small_blind is None and i > self.small_blind_player_i:
                    next_small_blind = len(new_players_info)
                new_players_info.append((self._players_info[i][0], balance))
        self._game_num += 1
        self.small_blind_player_i = 0 if next_small_blind is None \
                                        else next_small_blind
        self._players_info = new_players_info

    def play_game(
        self,
        on_player_turn: Callable[[dict, dict, dict], dict],
        on_new_game: Callable[[dict], None] | None = None,
        on_new_hand: Callable[[dict, dict], None] | None = None,
        on_round_start: Callable[[dict, dict], None] | None = None,
        on_round_end: Callable[[dict, dict, dict], None] | None = None,
        on_hand_end: Callable[[dict, dict], None] | None = None,
        on_game_end: Callable[[list[dict], dict, dict], None] | None = None
    ):
        if on_new_game:
            on_new_game(self.status)

        for hand in self.advance():
            if on_new_hand:
                on_new_hand(hand.status, self.status)

            while not hand.finalize_hand():
                if on_round_start:
                    on_round_start(hand.status, self.status)

                curr_round = hand.round()
                state = next(curr_round)
                while True:
                    # The caller must send the user_dict back
                    user_dict = on_player_turn(state, hand.status, self.status)
                    try:
                        state = curr_round.send(user_dict)
                    except StopIteration as e:
                        last_action = e.value
                        if on_round_end:
                            on_round_end(last_action, hand.status, self.status)
                        break

                if on_hand_end:
                    on_hand_end(hand.status, self.status)

            if on_game_end:
                on_game_end(hand.winners, hand.status, self.status)
