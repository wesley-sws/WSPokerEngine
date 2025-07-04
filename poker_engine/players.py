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
    def public_status(self) -> dict:
        return {
            'id': self.id,
            'balance': self.balance,
            'money_in': self.money_in,
            'folded': self.folded,
            'gone_max': self.gone_max,
            'initial_balance': self.initial_balance
        }

class AutonomousPlayer(Player):
    @abstractmethod
    def make_decision(self, state: dict, hand_status: dict, game_status: dict) -> dict:
        ''' 
        Assumes the following keys in the dictionaries:
        state: 
        - "current_bet", "options", "last_action_result"
        hand_status: 
        - "round_num", "revealed_comm_cards", "pot_size", "players_in", "current_player_pos"
        game_status: 
        - "players_info" (list of player statuses), "small_blind_player_pos",
          "blinds", "game_num"
        '''
        pass

class PlayerStats:
    player_id: int
    
