"""Pygame-free command handling and fixed-step scheduling."""

from enum import Enum
from random import Random
from typing import Iterable

from .core import GameStatus, Direction, new_game, request_direction, restart, tick, toggle_pause

TICK_MS = 125


class Command(Enum):
    PAUSE = "pause"
    RESTART = "restart"
    EXIT = "exit"


class Session:
    """Compose core commands with elapsed milliseconds supplied by an adapter."""

    def __init__(self, rng: Random):
        self.rng = rng
        self.state = new_game(rng)
        self.accumulator_ms = 0
        self.exit_requested = False

    def advance(self, elapsed_ms: int, commands: Iterable[Command | Direction] = ()) -> None:
        if elapsed_ms < 0:
            raise ValueError("Elapsed milliseconds must be nonnegative")
        if self.exit_requested:
            return
        discard_elapsed = False
        for command in commands:
            if command is Command.EXIT:
                self.exit_requested = True
                self.accumulator_ms = 0
                return
            if command is Command.RESTART:
                self.state = restart(self.state, self.rng)
                self.accumulator_ms = 0
                discard_elapsed = True
            elif command is Command.PAUSE:
                updated = toggle_pause(self.state)
                if updated.status is not self.state.status:
                    self.accumulator_ms = 0
                    discard_elapsed = True
                self.state = updated
            elif isinstance(command, Direction):
                self.state = request_direction(self.state, command)

        if self.state.status is not GameStatus.RUNNING:
            self.accumulator_ms = 0
            return
        if discard_elapsed:
            return
        self.accumulator_ms += elapsed_ms
        while self.accumulator_ms >= TICK_MS:
            self.state = tick(self.state, self.rng)
            self.accumulator_ms -= TICK_MS
            if self.state.status is not GameStatus.RUNNING:
                self.accumulator_ms = 0
                break
