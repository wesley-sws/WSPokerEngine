"""Constants and enums for the poker engine."""

from enum import Enum

class ActionType(Enum):
    """Player action types."""
    FOLD = "F"
    CALL = "C"
    RAISE = "R"
    ALL_IN = "A"