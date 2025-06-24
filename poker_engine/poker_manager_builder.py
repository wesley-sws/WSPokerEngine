from typing import Optional, Iterable
from .poker_manager import PokerManager
from .hand_manager import HandManager
from .players import Player

class PokerManagerBuilder:
    """Builder pattern for creating PokerManager instances with validation."""
    
    def __init__(self):
        self._blinds: Optional[list[int]] = None
        self._players: list[int] = []
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
    
    def add_player_by_balance(self, balance: int):
        """Add a player with specified balance and optional ID."""

        if balance <= 0:
            raise ValueError("Player balance must be positive")
        
        self._players.append(Player(balance))
        return self
    
    def add_players_by_balance(self, balances: Iterable[int]):
        """Add a player with specified balance and optional ID."""
        for balance in balances:
            self.add_player_by_balance(balance)
        return self
    
    def add_player(self, player: Player) -> 'PokerManagerBuilder':
        """Add a player with specified balance and optional ID."""
        if player.balance <= 0 or player.initial_balance <= 0:
            raise ValueError("Player balance must be positive")
        
        self._players.append(player)
        return self
    
    def add_players(self, players: Iterable[Player]) -> 'PokerManagerBuilder':
        for player in players:
            self.add_player(player)
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
            self._blinds,
            self._players,
            self._small_blind_index
        )
    
    def _validate(self) -> None:
        """Validate all required parameters are set correctly."""
        if self._blinds is None:
            raise ValueError("Blinds must be set using with_blinds()")
        
        if len(self._players) < HandManager.MIN_PLAYERS:
            raise ValueError("At least 2 players required")
        
        if len(self._players) > HandManager.MAX_PLAYERS:  # Assuming max from HandManager
            raise ValueError("Maximum 9 players allowed")
        
        if self._small_blind_index >= len(self._players):
            raise ValueError(f"Small blind position ({self._small_blind_index}) must be less than number of players ({len(self._player_balances)})")
        
        # Check if any player can cover at least the big blind
        big_blind = self._blinds[1]
        if not any(player.balance >= big_blind for player in self._players):
            raise ValueError(f"At least one player must have balance >= big blind ({big_blind})")