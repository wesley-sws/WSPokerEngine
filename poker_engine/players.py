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

    def get_player_status(self) -> dict:
        return asdict(self)
