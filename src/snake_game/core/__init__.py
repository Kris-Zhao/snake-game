"""Public deterministic core API; requires only the Python standard library."""

from .engine import new_game, request_direction, restart, tick, toggle_pause
from .model import Cell, Direction, GameState, GameStatus

__all__ = [
    "Cell", "Direction", "GameState", "GameStatus",
    "new_game", "request_direction", "restart", "tick", "toggle_pause",
]
