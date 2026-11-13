from dataclasses import replace
from random import Random

import pytest

from snake_game.application import Command, Session
from snake_game.core import Direction, GameStatus


def session():
    result = Session(Random(8))
    result.state = replace(result.state, food=(0, 0))
    return result


def test_tick_boundary_and_remainder():
    game = session()
    game.advance(124)
    assert game.state.snake[0] == (10, 10)
    assert game.accumulator_ms == 124
    game.advance(2)
    assert game.state.snake[0] == (11, 10)
    assert game.accumulator_ms == 1


def test_fixed_ticks_are_independent_of_render_frame_partition():
    first, second = session(), session()
    first.advance(375)
    for elapsed in (10, 100, 15, 200, 50):
        second.advance(elapsed)
    assert first.state == second.state
    assert first.state.snake[0] == (13, 10)
    assert first.accumulator_ms == second.accumulator_ms == 0


@pytest.mark.parametrize("commands", [
    [Command.RESTART], [Command.PAUSE, Command.PAUSE],
    [Direction.UP, Command.RESTART],
])
def test_reset_discards_fraction_and_current_elapsed(commands):
    game = session()
    game.advance(100)
    game.advance(1000, commands)
    assert game.state.snake[0] == (10, 10)
    assert game.accumulator_ms == 0
    game.advance(124)
    assert game.state.snake[0] == (10, 10)
    game.advance(1)
    assert game.state.snake[0] == (11, 10)


def test_pause_never_accumulates_time_and_resume_needs_fresh_interval():
    game = session()
    game.advance(110)
    game.advance(800, [Command.PAUSE])
    paused = game.state
    game.advance(100000, [Direction.UP])
    assert game.state == paused
    assert game.accumulator_ms == 0
    game.advance(1000, [Command.PAUSE])
    assert game.state.snake == paused.snake
    game.advance(125)
    assert game.state.snake[0] == (11, 10)


def test_restart_then_arrow_is_fresh_and_applies_after_reset_interval():
    game = session()
    game.advance(1000, [Direction.DOWN, Command.RESTART, Direction.UP])
    assert game.state.pending_direction is Direction.UP
    assert game.state.snake[0] == (10, 10)
    game.advance(125)
    assert game.state.snake[0] == (10, 9)


def test_restart_then_pause_leaves_fresh_paused_game():
    game = session()
    game.advance(500, [Command.RESTART, Command.PAUSE, Direction.UP])
    assert game.state.status is GameStatus.PAUSED
    assert game.state.pending_direction is None
    assert game.accumulator_ms == 0


@pytest.mark.parametrize("status", list(GameStatus))
def test_exit_is_immediate_from_any_state_and_ignores_later_commands(status):
    game = session()
    game.state = replace(game.state, status=status)
    original = game.state
    game.advance(100000, [Command.EXIT, Command.RESTART, Direction.UP])
    assert game.exit_requested
    assert game.state == original
    assert game.accumulator_ms == 0
    game.advance(100000, [Command.RESTART])
    assert game.state == original


def test_terminal_tick_clears_catchup_and_terminal_events_remain_responsive():
    game = session()
    game.state = replace(game.state, snake=((19, 10), (18, 10), (17, 10)))
    game.advance(10000)
    assert game.state.status is GameStatus.GAME_OVER
    assert game.accumulator_ms == 0
    game.advance(10000, [Command.PAUSE, Direction.UP])
    assert game.state.status is GameStatus.GAME_OVER
    assert game.accumulator_ms == 0
    game.advance(10000, [Command.RESTART])
    assert game.state.status is GameStatus.RUNNING
    assert game.state.snake[0] == (10, 10)


def test_negative_elapsed_is_rejected():
    with pytest.raises(ValueError):
        session().advance(-1)
