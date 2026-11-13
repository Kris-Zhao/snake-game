"""Translate Pygame events into commands, leaving rules to the core."""

import pygame

from ..application import Command
from ..core import Direction

KEY_COMMANDS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_SPACE: Command.PAUSE,
    pygame.K_r: Command.RESTART,
    pygame.K_ESCAPE: Command.EXIT,
}


def command_for_event(event: pygame.event.Event) -> Command | Direction | None:
    if event.type == pygame.QUIT:
        return Command.EXIT
    if event.type == pygame.KEYDOWN:
        return KEY_COMMANDS.get(event.key)
    return None
