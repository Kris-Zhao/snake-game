"""Independent acceptance checks for Feature 01's ordinary running ticks."""

from dataclasses import FrozenInstanceError, replace
from itertools import product
from random import Random, getstate

import pytest

from snake_game.core import Direction, new_game, request_direction, tick


# Literal coordinate expectations keep these checks independent of Direction.delta.
DELTAS = {
    Direction.UP: (0, -1),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0),
}


@pytest.mark.parametrize("committed", DELTAS)
def test_every_three_request_sequence_obeys_first_perpendicular_turn(committed):
    dx, dy = DELTAS[committed]
    initial = replace(
        new_game(Random(0)),
        snake=((10, 10), (10 - dx, 10 - dy), (10 - 2 * dx, 10 - 2 * dy)),
        direction=committed,
        food=(0, 0),
    )
    for requests in product(DELTAS, repeat=3):
        expected = committed
        for candidate in requests:
            cx, cy = DELTAS[candidate]
            if dx * cx + dy * cy == 0:
                expected = candidate
                break

        queued = initial
        for candidate in requests:
            queued = request_direction(queued, candidate)
            assert queued.snake == initial.snake, requests
            assert queued.direction is committed, requests
            assert queued.score == initial.score, requests
            assert queued.food == initial.food, requests

        moved = tick(queued, Random(0))
        ex, ey = DELTAS[expected]
        assert moved.snake == ((10 + ex, 10 + ey),) + initial.snake[:-1], requests
        assert moved.direction is expected, requests
        assert moved.pending_direction is None, requests

        # After committing, the opposite direction must still be rejected.
        opposite = next(d for d, delta in DELTAS.items() if delta == (-ex, -ey))
        assert request_direction(moved, opposite) == moved, requests


def test_injected_selector_and_ordinary_tick_do_not_use_global_randomness():
    class Selector:
        calls = 0

        def choice(self, cells):
            self.calls += 1
            assert self.calls == 1, "Ordinary ticks must not select food again"
            return cells[0]

    selector = Selector()
    random_before = getstate()
    state = new_game(selector)
    assert state.food == (0, 0)
    queued = request_direction(state, Direction.DOWN)
    first = tick(queued, selector)
    second = tick(first, selector)
    assert first.snake[0] == (10, 11)
    assert second.snake[0] == (10, 12)
    assert selector.calls == 1
    assert getstate() == random_before


def test_state_is_immutable_and_turn_request_preserves_input():
    state = new_game(Random(0))
    with pytest.raises(FrozenInstanceError):
        state.direction = Direction.UP
    queued = request_direction(state, Direction.UP)
    assert state.pending_direction is None
    assert queued == replace(state, pending_direction=Direction.UP)
