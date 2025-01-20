from hand_manager import HandManager

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
    
    def get_status(self):
        # note only gets updated AFTER a round
        return self.__dict__()
    
    def advance(self):
        while len(self.players_info) > 1:
            new_hand = HandManager(
                self.players_info,
                self.small_blind_player_i, self.blinds, self.game_num
            )
            yield new_hand
            self.update_player_info(new_hand.get_players_balance())

    def update_player_info(self, updated_balance):
        new_players_info = []
        next_small_blind = None
        for i, balance in enumerate(updated_balance):
            if balance != 0:
                if next_small_blind is None and i > self.small_blind_player_i:
                    next_small_blind = len(new_players_info)
                new_players_info.append((self.players_info[i][0], balance))
        self.game_num += 1
        self.small_blind_player_i = 0 if next_small_blind is None else next_small_blind
        self.players_info = new_players_info
