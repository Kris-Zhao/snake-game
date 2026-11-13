from dataclasses import replace
from random import Random

import pygame
import pytest

from snake_game.application import Command, Session
from snake_game.core import Direction, GameStatus
from snake_game.rendering.input import command_for_event


@pytest.mark.parametrize("key,expected", [
    (pygame.K_UP, Direction.UP), (pygame.K_DOWN, Direction.DOWN),
    (pygame.K_LEFT, Direction.LEFT), (pygame.K_RIGHT, Direction.RIGHT),
    (pygame.K_SPACE, Command.PAUSE), (pygame.K_r, Command.RESTART),
    (pygame.K_ESCAPE, Command.EXIT),
])
def test_keyboard_translation(key, expected):
    assert command_for_event(pygame.event.Event(pygame.KEYDOWN, key=key)) is expected


def test_only_keydown_or_quit_produces_commands():
    assert command_for_event(pygame.event.Event(pygame.QUIT)) is Command.EXIT
    assert command_for_event(pygame.event.Event(pygame.KEYUP, key=pygame.K_UP)) is None
    assert command_for_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)) is None


def test_arrow_batch_obeys_core_reversal_and_first_turn_rules():
    game = Session(Random(4))
    commands = [command_for_event(pygame.event.Event(pygame.KEYDOWN, key=key))
                for key in (pygame.K_LEFT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN)]
    game.advance(125, commands)
    assert game.state.snake[0] == (10, 9)
    assert game.state.direction is Direction.UP


@pytest.mark.parametrize("status", list(GameStatus))
def test_r_restarts_every_status(status):
    game = Session(Random(4))
    game.state = replace(game.state, status=status, score=70, pending_direction=Direction.UP)
    game.advance(1000, [command_for_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))])
    assert game.state.status is GameStatus.RUNNING
    assert game.state.score == 0
    assert game.state.pending_direction is None
    assert game.state.snake[0] == (10, 10)
