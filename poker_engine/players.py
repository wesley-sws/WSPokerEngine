from .cards import Card
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import Optional

'''Assume use is single threaded (so no need for id_lock)'''
class Player:
    _next_id = 0
    @classmethod
    def new_id(cls) -> int:
        cls._next_id += 1
        return cls._next_id - 1
    def reset_round(self):
        self.initial_balance: int = self.balance
        self.money_in: int = 0
        self.hands: Optional[tuple[Card]] = None
        self.folded: bool = False
        self.gone_max: bool = False
        
    def __init__(self, initial_balance: int):
        self.balance: int = initial_balance
        self.id = Player.new_id()
        self.reset_round()

    @property
    def status(self) -> dict:
        return vars(self)
    
    # @abstractmethod
    # def make_decision(hand_status, current_bet, options, last_action):
    #     ...

class PlayerStats:
    player_id: int
    
