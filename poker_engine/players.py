from cards import Card
from dataclasses import dataclass, asdict

@dataclass
class Player:
    id: int
    balance: int
    money_in: int
    hands: tuple[Card]
    folded: bool = False
    gone_max: bool = False

    def get_player_status(self, include_hand: bool) -> dict:
        # Convert all attributes to a dictionary
        res = asdict(self)
        # Optionally exclude 'hands'
        if not include_hand:
            res.pop("hands")
        return res
