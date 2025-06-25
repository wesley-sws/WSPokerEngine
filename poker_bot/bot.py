from poker_engine.players import Player
class Bot(Player):
    def make_decision(self, state, hand_status, game_status) -> dict:
        ...