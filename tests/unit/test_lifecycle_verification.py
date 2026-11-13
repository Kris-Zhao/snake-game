"""Independent Feature 03 checks derived from the approved lifecycle contract."""

from dataclasses import asdict, replace
from random import Random, getstate

import pytest

from snake_game.core import (
    Direction, GameState, GameStatus, new_game, request_direction, restart,
    tick, toggle_pause,
)


class NoSelection:
    def choice(self, cells):
        raise AssertionError("This transition must not select food")


@pytest.mark.parametrize("turn,target", [
    (Direction.UP, (10, 9)), (Direction.DOWN, (10, 11)),
])
def test_pending_turn_survives_repeated_pause_cycles_and_can_eat(turn, target):
    initial = replace(new_game(Random(7)), food=target, score=30)
    snapshot = asdict(initial)
    queued = request_direction(initial, turn)
    global_before = getstate()
    for _ in range(5):
        paused = toggle_pause(queued)
        assert paused == replace(queued, status=GameStatus.PAUSED)
        for direction in Direction:
            paused = request_direction(paused, direction)
            paused = tick(paused, NoSelection())
        assert paused.pending_direction is turn
        queued = toggle_pause(paused)
        assert queued == request_direction(initial, turn)

    class FoodSelector:
        calls = 0

        def choice(self, cells):
            self.calls += 1
            assert target not in cells
            return (0, 0)

    selector = FoodSelector()
    moved = tick(queued, selector)
    assert moved.snake == (target,) + initial.snake
    assert moved.score == 40
    assert moved.food == (0, 0)
    assert moved.direction is turn
    assert moved.pending_direction is None
    assert selector.calls == 1
    # The one-turn allowance reopens after this tick.
    next_move = tick(request_direction(moved, Direction.LEFT), NoSelection())
    assert next_move.snake[0] == (9, target[1])
    assert asdict(initial) == snapshot
    assert getstate() == global_before


def test_restart_sequence_matches_independent_rng_food_oracle():
    rng, oracle = Random(173), Random(173)
    # Advance both generators before use so silently reseeding is observable.
    for _ in range(7):
        rng.random()
        oracle.random()
    default_snake = ((10, 10), (9, 10), (8, 10))
    free_cells = [(x, y) for y in range(20) for x in range(20)
                  if (x, y) not in default_snake]
    original = GameState(4, 3, ((2, 1), (1, 1), (0, 1)),
                         Direction.DOWN, Direction.LEFT, (3, 2), 90,
                         GameStatus.PAUSED)
    snapshot = asdict(original)
    global_before = getstate()
    for status in GameStatus:
        restarted = restart(replace(original, status=status), rng)
        assert restarted == GameState(20, 20, default_snake, Direction.RIGHT,
                                      None, oracle.choice(free_cells), 0,
                                      GameStatus.RUNNING)
        assert rng.getstate() == oracle.getstate()
        # A newly supplied turn works immediately after restart.
        moved = tick(request_direction(restarted, Direction.UP), NoSelection())
        assert moved.snake == ((10, 9), (10, 10), (9, 10))
    assert asdict(original) == snapshot
    assert getstate() == global_before


@pytest.mark.parametrize("terminal", [GameStatus.GAME_OVER, GameStatus.WON])
def test_reached_terminal_state_cannot_resume_but_can_restart(terminal):
    if terminal is GameStatus.WON:
        initial = GameState(2, 2, ((1, 0), (0, 0), (0, 1)),
                            Direction.RIGHT, Direction.DOWN, (1, 1), 20,
                            GameStatus.RUNNING)
    else:
        initial = GameState(3, 2, ((2, 0), (1, 0), (0, 0)),
                            Direction.RIGHT, None, (2, 1), 20,
                            GameStatus.RUNNING)
    ended = tick(initial, NoSelection())
    assert ended.status is terminal
    for _ in range(4):
        assert toggle_pause(ended) is ended
        for direction in Direction:
            assert request_direction(ended, direction) is ended
        assert tick(ended, NoSelection()) is ended
    fresh = restart(ended, Random(42))
    assert fresh.status is GameStatus.RUNNING
    assert fresh.pending_direction is None
    assert fresh.score == 0
    assert fresh.food not in fresh.snake
    assert ended.status is terminal
