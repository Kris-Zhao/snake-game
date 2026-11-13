import os
from pathlib import Path
import subprocess
import sys

import pytest

from snake_game import app


class FixedClock:
    def tick(self, fps):
        assert fps == 60
        return 16


def test_finite_dummy_run_draws_and_closes(pygame_ready, monkeypatch):
    pygame = pygame_ready
    monkeypatch.setattr(pygame.time, "Clock", FixedClock)
    flips = []
    original_flip = pygame.display.flip

    def flip():
        assert pygame.display.get_surface().get_size() == (600, 724)
        flips.append(True)
        original_flip()

    monkeypatch.setattr(pygame.display, "flip", flip)
    result = app.run(max_frames=3)
    assert len(flips) == 3
    assert result.snake[0] == (10, 10)
    assert not pygame.get_init()
    assert pygame.display.get_surface() is None


@pytest.mark.parametrize("exit_type", ["quit", "escape"])
def test_exit_stops_without_drawing(pygame_ready, monkeypatch, exit_type):
    pygame = pygame_ready
    event = (pygame.event.Event(pygame.QUIT) if exit_type == "quit"
             else pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    monkeypatch.setattr(pygame.event, "get", lambda: [event])
    monkeypatch.setattr(pygame.time, "Clock", FixedClock)
    monkeypatch.setattr(app.GameView, "draw", lambda *args: pytest.fail("Drew after exit"))
    app.run(max_frames=3)
    assert not pygame.get_init()


@pytest.mark.parametrize("failure_point", ["init", "display", "draw"])
def test_errors_propagate_but_always_quit(pygame_ready, monkeypatch, failure_point):
    pygame = pygame_ready

    def fail(*args, **kwargs):
        raise RuntimeError("injected failure")

    monkeypatch.setattr(pygame.time, "Clock", FixedClock)
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    if failure_point == "init":
        monkeypatch.setattr(pygame, "init", fail)
    elif failure_point == "display":
        monkeypatch.setattr(pygame.display, "set_mode", fail)
    else:
        monkeypatch.setattr(app.GameView, "draw", fail)
    with pytest.raises(RuntimeError, match="injected failure"):
        app.run(max_frames=1)
    assert not pygame.get_init()


def test_importing_every_module_is_inert():
    source_root = Path(__file__).resolve().parents[2] / "src"
    script = """
import importlib
import pkgutil
import pygame
import snake_game
for module in pkgutil.walk_packages(snake_game.__path__, snake_game.__name__ + '.'):
    importlib.import_module(module.name)
assert not pygame.get_init()
assert not pygame.display.get_init()
assert pygame.display.get_surface() is None
"""
    result = subprocess.run([sys.executable, "-c", script],
                            env=dict(os.environ, PYTHONPATH=str(source_root)),
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
