import os
from pathlib import Path
import subprocess
import sys


def test_core_runs_without_pygame_or_site_packages():
    source_root = Path(__file__).resolve().parents[2] / "src"
    script = """
import importlib.abc
import sys
from random import Random

class BlockPygame(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == 'pygame' or fullname.startswith('pygame.'):
            raise ImportError('Pygame intentionally unavailable')

sys.meta_path.insert(0, BlockPygame())
import snake_game
from snake_game.core import new_game, tick, request_direction, Direction, toggle_pause, restart
state = new_game(Random(1))
state = tick(request_direction(state, Direction.UP), Random(2))
assert state.snake[0] == (10, 9)
paused = toggle_pause(state)
assert tick(paused, Random(3)) == paused
assert toggle_pause(paused) == state
state = restart(paused, Random(4))
assert state.direction is Direction.RIGHT
assert state.pending_direction is None
assert not any(name == 'pygame' or name.startswith('pygame.') for name in sys.modules)
"""
    env = dict(os.environ, PYTHONPATH=str(source_root))
    result = subprocess.run(
        [sys.executable, "-S", "-c", script],
        env=env, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
