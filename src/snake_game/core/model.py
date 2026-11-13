"""Immutable, presentation-independent game state."""

from dataclasses import dataclass
from enum import Enum

Cell = tuple[int, int]


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self) -> Cell:
        return self.value


class GameStatus(Enum):
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    WON = "won"


@dataclass(frozen=True)
class GameState:
    """Snake cells are ordered head first; coordinates use x right, y down."""

    width: int
    height: int
    snake: tuple[Cell, ...]
    direction: Direction
    pending_direction: Direction | None
    food: Cell | None
    score: int
    status: GameStatus
