from typing import Optional
from .poker_manager import PokerManager
from .hand_manager import HandManager

class PokerManagerBuilder:
    """Builder pattern for creating PokerManager instances with validation."""
    
    def __init__(self):
        self._blinds: Optional[list[int]] = None
        self._player_balances: list[int] = []
        self._player_ids: Optional[list[int]] = None
        self._small_blind_index: int = 0
    
    def with_blinds(self, small_blind: int, big_blind: int) -> 'PokerManagerBuilder':
        """Set the blind amounts."""
        if small_blind <= 0 or big_blind <= 0:
            raise ValueError("Blinds must be positive")
        if small_blind >= big_blind:
            raise ValueError("Small blind must be less than big blind")
        
        self._blinds = [small_blind, big_blind]
        return self
    
    def add_player(self, balance: int, player_id: Optional[int] = None) -> 'PokerManagerBuilder':
        """Add a player with specified balance and optional ID."""
        if balance <= 0:
            raise ValueError("Player balance must be positive")
        
        self._player_balances.append(balance)
        
        if player_id is not None:
            if self._player_ids is None:
                # First player with custom ID - initialize list
                self._player_ids = list(range(len(self._player_balances) - 1))
            self._player_ids.append(player_id)
        elif self._player_ids is not None:
            # Auto-generate ID if we're using custom IDs
            next_id = max(self._player_ids) + 1 if self._player_ids else 0
            self._player_ids.append(next_id)
        
        return self
    
    def add_players(self, balances: list[int], player_ids: Optional[list[int]] = None) -> 'PokerManagerBuilder':
        """Add multiple players at once."""
        if player_ids and len(balances) != len(player_ids):
            raise ValueError("Number of balances must match number of player IDs")
        
        for i, balance in enumerate(balances):
            player_id = player_ids[i] if player_ids else None
            self.add_player(balance, player_id)
        
        return self
    
    def with_small_blind_position(self, position: int) -> 'PokerManagerBuilder':
        """Set which player position starts as small blind (0-indexed)."""
        if position < 0:
            raise ValueError("Small blind position must be non-negative")
        
        self._small_blind_index = position
        return self
    
    def build(self) -> PokerManager:
        """Build and return the PokerManager instance."""
        self._validate()
        
        return PokerManager(
            blinds=self._blinds,
            player_balance=self._player_balances,
            player_ids=self._player_ids,
            small_blind_i=self._small_blind_index
        )
    
    def _validate(self) -> None:
        """Validate all required parameters are set correctly."""
        if self._blinds is None:
            raise ValueError("Blinds must be set using with_blinds()")
        
        if len(self._player_balances) < HandManager.MIN_PLAYERS:
            raise ValueError("At least 2 players required")
        
        if len(self._player_balances) > HandManager.MAX_PLAYERS:  # Assuming max from HandManager
            raise ValueError("Maximum 9 players allowed")
        
        if self._small_blind_index >= len(self._player_balances):
            raise ValueError(f"Small blind position ({self._small_blind_index}) must be less than number of players ({len(self._player_balances)})")
        
        if self._player_ids and len(set(self._player_ids)) != len(self._player_ids):
            raise ValueError("Player IDs must be unique")
        
        # Check if any player can cover at least the big blind
        big_blind = self._blinds[1]
        if not any(balance >= big_blind for balance in self._player_balances):
            raise ValueError(f"At least one player must have balance >= big blind ({big_blind})")