from dataclasses import replace
from random import Random

import pytest

from snake_game.core import Direction, new_game, request_direction, tick


@pytest.mark.parametrize("direction", [Direction.UP, Direction.DOWN])
def test_perpendicular_turn_applies_only_on_next_tick(direction):
    rng = Random(1)
    state = replace(new_game(rng), food=(0, 0))
    queued = request_direction(state, direction)
    assert queued.snake == state.snake
    assert queued.direction is Direction.RIGHT
    assert queued.pending_direction is direction
    result = tick(queued, rng)
    dx, dy = direction.delta
    assert result.snake[0] == (10 + dx, 10 + dy)
    assert result.direction is direction
    assert result.pending_direction is None


@pytest.mark.parametrize("ignored", [Direction.LEFT, Direction.RIGHT])
def test_ignored_request_does_not_consume_turn(ignored):
    state = new_game(Random(1))
    assert request_direction(state, ignored) == state
    queued = request_direction(request_direction(state, ignored), Direction.UP)
    assert queued.pending_direction is Direction.UP


def test_first_valid_turn_wins_and_tick_resets_allowance():
    rng = Random(1)
    state = replace(new_game(rng), food=(0, 0))
    queued = request_direction(state, Direction.UP)
    for direction in Direction:
        queued = request_direction(queued, direction)
        assert queued.pending_direction is Direction.UP
    state = tick(queued, rng)
    assert state.snake[0] == (10, 9)
    state = tick(request_direction(state, Direction.LEFT), rng)
    assert state.direction is Direction.LEFT
    assert state.snake[0] == (9, 9)
