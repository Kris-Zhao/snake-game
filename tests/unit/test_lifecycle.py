from dataclasses import replace
from random import Random, getstate

import pytest

from snake_game.core import (
    Direction, GameStatus, new_game, request_direction, restart, tick, toggle_pause,
)


class NoRandom:
    def choice(self, cells):
        raise AssertionError("Inactive commands must not use randomness")


def test_pause_and_resume_change_only_status_and_preserve_pending_turn():
    original = replace(new_game(Random(4)), food=(0, 0))
    queued = request_direction(original, Direction.UP)
    paused = toggle_pause(queued)
    assert paused == replace(queued, status=GameStatus.PAUSED)
    assert tick(paused, NoRandom()) is paused
    assert request_direction(paused, Direction.DOWN) is paused
    resumed = toggle_pause(paused)
    assert resumed == queued
    result = tick(resumed, NoRandom())
    assert result.snake[0] == (10, 9)
    assert result.direction is Direction.UP
    assert result.pending_direction is None
    assert original.pending_direction is None


def test_paused_direction_does_not_appear_after_resume():
    state = replace(new_game(Random(4)), food=(0, 0))
    paused = toggle_pause(state)
    paused = request_direction(paused, Direction.DOWN)
    result = tick(toggle_pause(paused), NoRandom())
    assert result.direction is Direction.RIGHT
    assert result.snake[0] == (11, 10)


@pytest.mark.parametrize("status", [GameStatus.PAUSED, GameStatus.GAME_OVER, GameStatus.WON])
@pytest.mark.parametrize("pending", [None, Direction.UP])
def test_inactive_ticks_and_every_direction_are_ignored(status, pending):
    state = replace(new_game(Random(3)), status=status, pending_direction=pending)
    global_before = getstate()
    for _ in range(3):
        assert tick(state, NoRandom()) is state
        for direction in Direction:
            assert request_direction(state, direction) is state
    assert getstate() == global_before


@pytest.mark.parametrize("status", [GameStatus.GAME_OVER, GameStatus.WON])
def test_pause_toggle_cannot_resume_terminal_state(status):
    state = replace(new_game(Random(3)), status=status)
    assert toggle_pause(state) is state


@pytest.mark.parametrize("status", list(GameStatus))
def test_restart_resets_all_game_fields_from_any_status(status):
    state = replace(
        new_game(Random(3)), width=6, height=5,
        snake=((2, 1), (2, 2), (1, 2), (1, 1)),
        direction=Direction.UP, pending_direction=Direction.LEFT,
        score=50, status=status, food=(5, 4),
    )
    result = restart(state, Random(9))
    assert result == new_game(Random(9))
    assert (result.width, result.height) == (20, 20)
    assert result.snake == ((10, 10), (9, 10), (8, 10))
    assert result.direction is Direction.RIGHT
    assert result.pending_direction is None
    assert result.status is GameStatus.RUNNING
    assert result.score == 0
    assert result.food not in result.snake
    assert state.score == 50
    assert state.status is status
    result = replace(result, food=(0, 0))
    assert tick(result, NoRandom()).snake[0] == (11, 10)


def test_restart_uses_existing_rng_stream_without_reseeding_or_global_randomness():
    rng = Random(51)
    expected_rng = Random(51)
    state = new_game(rng)
    new_game(expected_rng)
    global_before = getstate()
    assert restart(state, rng) == new_game(expected_rng)
    assert rng.getstate() == expected_rng.getstate()
    assert getstate() == global_before


def test_restart_selects_food_once_from_default_free_cells():
    class Recorder:
        calls = 0

        def choice(self, cells):
            self.calls += 1
            assert cells == [
                (x, y) for y in range(20) for x in range(20)
                if (x, y) not in ((10, 10), (9, 10), (8, 10))
            ]
            return cells[0]

    rng = Recorder()
    result = restart(new_game(Random(1)), rng)
    assert result.food == (0, 0)
    assert rng.calls == 1
