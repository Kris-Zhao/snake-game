# Snake

A local Python 3.12 / Pygame Snake game with independently testable rules.

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m snake_game
```

On other platforms, create the environment with `python3.12 -m venv .venv`
and use `.venv/bin/python` for the install and launch commands.

Use arrow keys to turn, Space to pause/resume, R to restart, and Escape or the
window close button to exit. The 20×20 board starts with three snake cells
moving right at eight ticks per second. Each food grows the snake by one cell
and adds ten points. Walls and body collisions end the game; filling the board
wins. One valid turn is accepted per tick, direct reversals are ignored, and
arrows are ignored while paused or after the game ends.

Run verification with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit
.\.venv\Scripts\python.exe -m pytest
```

Core tests need neither Pygame nor a display. Integration tests use scoped SDL
dummy drivers. A finite graphical smoke run is also available:

```powershell
.\.venv\Scripts\python.exe -c "from snake_game.app import run; run(max_frames=3)"
```

The finite run checks window creation, drawing, and shutdown; physical keyboard
interaction and visual readability still require playing the game in a real window.
