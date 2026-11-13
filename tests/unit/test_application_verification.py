"""Independent acceptance checks for frame timing and ordered commands."""

from dataclasses import replace
from random import Random

import pytest

from snake_game.application import Command, Session
from snake_game.core import Direction, GameStatus


def game():
    session = Session(Random(51))
    session.state = replace(session.state, food=(0, 0))
    return session


@pytest.mark.parametrize("status", list(GameStatus))
def test_restart_from_each_status_requires_entire_new_interval(status):
    session = game()
    session.advance(124)
    session.state = replace(session.state, status=status, score=90,
                            pending_direction=Direction.DOWN)
    session.advance(100000, [Direction.UP, Command.RESTART])
    assert session.state.status is GameStatus.RUNNING
    assert session.state.snake == ((10, 10), (9, 10), (8, 10))
    assert session.state.direction is Direction.RIGHT
    assert session.state.score == 0
    assert session.state.pending_direction is None
    assert session.state.food not in session.state.snake
    assert session.accumulator_ms == 0
    session.advance(124)
    assert session.state.snake[0] == (10, 10)
    session.advance(1)
    assert session.state.snake[0] == (11, 10)


@pytest.mark.parametrize("status", [GameStatus.PAUSED, GameStatus.GAME_OVER, GameStatus.WON])
def test_inactive_frames_preserve_entire_state_and_rng(status):
    session = game()
    session.state = replace(session.state, status=status, score=30)
    before, rng_before = session.state, session.rng.getstate()
    for elapsed in (124, 1, 375, 100000):
        session.advance(elapsed, list(Direction))
        assert session.state == before
        assert session.rng.getstate() == rng_before
        assert session.accumulator_ms == 0
    if status is not GameStatus.PAUSED:
        session.advance(100000, [Command.PAUSE])
        assert session.state == before


def test_pause_batch_ignores_paused_arrow_then_accepts_arrow_after_resume():
    session = game()
    session.advance(124)
    session.advance(10000, [Command.PAUSE, Direction.DOWN, Command.PAUSE,
                            Direction.UP, Direction.LEFT])
    assert session.state.snake[0] == (10, 10)
    assert session.state.pending_direction is Direction.UP
    assert session.accumulator_ms == 0
    session.advance(124)
    assert session.state.snake[0] == (10, 10)
    session.advance(1)
    assert session.state.snake[0] == (10, 9)


def test_partitioned_frames_retain_fraction_and_rng_through_food_tick():
    first, second = game(), game()
    for session in (first, second):
        session.state = replace(session.state, food=(11, 10))
    first.advance(499)
    for elapsed in (1, 123, 1, 40, 84, 0, 125, 125):
        second.advance(elapsed)
    assert first.state == second.state
    assert first.state.snake[0] == (13, 10)
    assert first.state.score == 10
    assert len(first.state.snake) == 4
    assert first.accumulator_ms == second.accumulator_ms == 124
    assert first.rng.getstate() == second.rng.getstate()


def test_victory_clears_catchup_and_restart_remains_available():
    session = game()
    session.state = replace(session.state, width=2, height=2,
                            snake=((0, 0), (0, 1), (1, 1)), food=(1, 0))
    session.advance(100000)
    assert session.state.status is GameStatus.WON
    assert session.state.food is None
    assert session.state.score == 10
    assert session.accumulator_ms == 0
    won = session.state
    session.advance(100000, [Command.PAUSE, Direction.DOWN])
    assert session.state == won
    session.advance(100000, [Command.RESTART, Direction.UP])
    assert session.state.status is GameStatus.RUNNING
    assert session.state.snake[0] == (10, 10)
    session.advance(125)
    assert session.state.snake[0] == (10, 9)
