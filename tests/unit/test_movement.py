from dataclasses import replace
from random import Random

import pytest

from snake_game.core import Direction, new_game, tick


@pytest.mark.parametrize("direction", list(Direction))
def test_tick_moves_one_cell_and_removes_tail(direction):
    rng = Random(1)
    dx, dy = direction.delta
    snake = tuple((10 - offset * dx, 10 - offset * dy) for offset in range(3))
    state = replace(new_game(rng), snake=snake, direction=direction, food=(0, 0))
    result = tick(state, rng)
    assert result.snake == ((10 + dx, 10 + dy),) + state.snake[:-1]
    assert len(result.snake) == len(state.snake)
    assert result.score == state.score
    assert result.food == state.food
    assert state.snake == snake


def test_each_tick_advances_exactly_once():
    rng = Random(1)
    state = replace(new_game(rng), food=(0, 0))
    for x in range(11, 16):
        state = tick(state, rng)
        assert state.snake[0] == (x, 10)
        assert len(state.snake) == 3
