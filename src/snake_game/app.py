"""Explicit Pygame lifetime and responsive render loop."""

from random import Random

import pygame

from .application import Session
from .core import GameState
from .rendering.input import command_for_event
from .rendering.view import GameView, window_size


def run(max_frames: int | None = None) -> GameState:
    """Run interactively, or for a finite number of frames for smoke checks."""
    try:
        if max_frames is not None and max_frames < 0:
            raise ValueError("max_frames must be nonnegative or None")
        pygame.init()
        session = Session(Random())
        screen = pygame.display.set_mode(window_size(session.state))
        pygame.display.set_caption("Snake")
        view = GameView()
        clock = pygame.time.Clock()
        frames = 0
        while max_frames is None or frames < max_frames:
            elapsed_ms = clock.tick(60)
            commands = [
                command for event in pygame.event.get()
                if (command := command_for_event(event)) is not None
            ]
            session.advance(elapsed_ms, commands)
            if session.exit_requested:
                break
            view.draw(screen, session.state)
            pygame.display.flip()
            frames += 1
        return session.state
    finally:
        pygame.quit()
