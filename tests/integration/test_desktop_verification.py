"""Independent tests of the actual event loop, drawing and import boundaries."""

from dataclasses import replace
import os
from pathlib import Path
from random import Random
import subprocess
import sys

import pytest

from snake_game import app
from snake_game.application import Session
from snake_game.core import Direction, GameStatus, new_game
from snake_game.rendering import view


@pytest.mark.parametrize("status", list(GameStatus))
@pytest.mark.parametrize("exit_key", [None, "escape"])
def test_real_loop_exits_every_status_before_simulation_or_drawing(
        pygame_ready, monkeypatch, status, exit_key):
    pygame = pygame_ready
    session = Session(Random(20))
    session.state = replace(session.state, status=status)
    before = session.state
    monkeypatch.setattr(app, "Session", lambda rng: session)
    event = (pygame.event.Event(pygame.QUIT) if exit_key is None else
             pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    monkeypatch.setattr(pygame.event, "get", lambda: [event,
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)])

    class Clock:
        def tick(self, fps):
            return 10000

    monkeypatch.setattr(pygame.time, "Clock", Clock)
    monkeypatch.setattr(app.GameView, "draw", lambda *args: pytest.fail("draw after exit"))
    assert app.run(max_frames=1) == before
    assert session.exit_requested
    assert not pygame.get_init()
    assert pygame.display.get_surface() is None


@pytest.mark.parametrize("keys,expected_head,status", [
    (["up", "r"], (11, 10), GameStatus.RUNNING),
    (["r", "up"], (10, 9), GameStatus.RUNNING),
    (["space", "up"], (10, 10), GameStatus.PAUSED),
    (["space", "space", "down"], (10, 11), GameStatus.RUNNING),
    (["r", "space"], (10, 10), GameStatus.PAUSED),
])
def test_real_loop_preserves_event_order_and_transition_frame_reset(
        pygame_ready, monkeypatch, keys, expected_head, status):
    pygame = pygame_ready
    elapsed = iter((10000, 124, 1))
    key_codes = {"up": pygame.K_UP, "down": pygame.K_DOWN,
                 "space": pygame.K_SPACE, "r": pygame.K_r}
    batches = iter(([pygame.event.Event(pygame.KEYDOWN, key=key_codes[key])
                     for key in keys], [], []))

    class Clock:
        def tick(self, fps):
            assert fps == 60
            return next(elapsed)

    monkeypatch.setattr(pygame.time, "Clock", Clock)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    frames = []
    draw = app.GameView.draw

    def record(self, surface, state):
        frames.append(state)
        draw(self, surface, state)

    monkeypatch.setattr(app.GameView, "draw", record)
    result = app.run(max_frames=3)
    assert len(frames) == 3
    assert frames[0].snake[0] == frames[1].snake[0] == (10, 10)
    assert result.snake[0] == expected_head
    assert result.status is status
    assert not pygame.get_init()


def assert_text_pixels(pygame, surface, text, font, position):
    """Check that actual visible pixels include the expected text raster."""
    rendered = font.render(text, True, view.TEXT_COLOR)
    expected = pygame.Surface(rendered.get_size())
    expected.fill(view.BACKGROUND)
    expected.blit(rendered, (0, 0))
    rectangle = pygame.Rect(position, rendered.get_size())
    assert pygame.image.tobytes(surface.subsurface(rectangle), "RGB") == pygame.image.tobytes(expected, "RGB")


@pytest.mark.parametrize("status,label,help_text", [
    (GameStatus.RUNNING, None, None),
    (GameStatus.PAUSED, "Paused", "Space to resume"),
    (GameStatus.GAME_OVER, "Game over", "R to restart"),
    (GameStatus.WON, "You won!", "R to restart"),
])
def test_score_and_state_messages_reach_actual_surface(pygame_ready, status, label, help_text):
    pygame = pygame_ready
    state = replace(new_game(Random(2)), status=status, score=170,
                    food=None if status is GameStatus.WON else (0, 0))
    surface = pygame.display.set_mode(view.window_size(state))
    renderer = view.GameView()
    renderer.draw(surface, state)
    assert_text_pixels(pygame, surface, "Score: 170", renderer.text_font, (view.MARGIN, 60))
    if label:
        board = pygame.Rect(view.MARGIN, view.BOARD_TOP,
                            state.width * view.CELL_SIZE, state.height * view.CELL_SIZE)
        panel = pygame.Rect(0, 0, 340, 120)
        panel.center = board.center
        for index, (text, font) in enumerate(((label, renderer.overlay_font),
                                              (help_text, renderer.text_font))):
            rect = font.render(text, True, view.TEXT_COLOR).get_rect(
                center=(panel.centerx, panel.top + 36 + index * 43))
            assert_text_pixels(pygame, surface, text, font, rect.topleft)


def test_every_module_import_avoids_even_transient_initialization():
    source = Path(__file__).resolve().parents[2] / "src"
    script = """
import importlib
import pkgutil
import pygame
def forbidden(*args, **kwargs):
    raise AssertionError('Import attempted Pygame initialization or event loop')
pygame.init = forbidden
pygame.display.init = forbidden
pygame.display.set_mode = forbidden
pygame.font.init = forbidden
pygame.event.get = forbidden
pygame.time.Clock = forbidden
import snake_game
modules = [entry.name for entry in pkgutil.walk_packages(snake_game.__path__, 'snake_game.')]
assert 'snake_game.__main__' in modules
assert 'snake_game.core.engine' in modules
for name in modules:
    importlib.import_module(name)
assert not pygame.get_init()
assert not pygame.display.get_init()
"""
    result = subprocess.run([sys.executable, "-c", script],
                            env=dict(os.environ, PYTHONPATH=str(source)),
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("point", ["font", "clock", "events", "flip"])
def test_additional_loop_failures_propagate_and_release_display(pygame_ready, monkeypatch, point):
    pygame = pygame_ready

    def fail(*args, **kwargs):
        raise RuntimeError("verification failure " + point)

    class Clock:
        def tick(self, fps):
            return 16

    monkeypatch.setattr(pygame.time, "Clock", Clock)
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    if point == "font":
        monkeypatch.setattr(pygame.font, "Font", fail)
    elif point == "clock":
        monkeypatch.setattr(pygame.time, "Clock", fail)
    elif point == "events":
        monkeypatch.setattr(pygame.event, "get", fail)
    else:
        monkeypatch.setattr(pygame.display, "flip", fail)
    with pytest.raises(RuntimeError, match="verification failure " + point):
        app.run(max_frames=1)
    assert not pygame.get_init()
    assert not pygame.font.get_init()
    assert pygame.display.get_surface() is None
