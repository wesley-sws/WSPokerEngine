class PokerManager:
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
# TexasHoldem(5, [5, 10], [200, 300, 400, 500, 600]).play()
