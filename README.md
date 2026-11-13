# Snake Game

This is a local, single-player desktop Snake game built with Python 3.12 and Pygame. Guide the snake to eat food and score points while avoiding walls and its own body. Game rules are separate from the graphical interface, so the core logic can be tested without opening a window.

## Gameplay

- The board is 20 × 20 cells. The snake starts three cells long and moves to the right.
- The snake moves eight cells per second. Each piece of food increases its length by one cell and adds 10 points.
- Hitting a wall or the snake's body ends the game. Filling the entire board wins the game.
- At most one valid turn is accepted before each move. The snake cannot reverse direction directly.
- Arrow keys have no effect while the game is paused or after it ends.

| Key | Action |
| --- | --- |
| Arrow keys ↑ ↓ ← → | Change the snake's direction |
| Space | Pause or resume the game |
| R | Restart the game |
| Esc | Quit the game |
| Window close button | Quit the game |

## Running the Game

Install **Python 3.12** before running the game. A graphical desktop environment is required, and installing dependencies requires an internet connection to download Pygame.

Run all commands below from the project root (the directory containing `pyproject.toml`). Create a virtual environment and install dependencies before the first run. For subsequent runs, use the launch command directly.

### Windows (PowerShell)

Create a virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Launch the game:

```powershell
.\.venv\Scripts\python.exe -m snake_game
```

### macOS / Linux

Create a virtual environment and install dependencies:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
```

Launch the game:

```bash
.venv/bin/python -m snake_game
```

A game window opens on launch, and the snake starts moving automatically. Use the arrow keys to steer.

## Development and Testing

To run tests, install the development dependencies, which include pytest. On Windows, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest tests/unit
.\.venv\Scripts\python.exe -m pytest
```

On macOS / Linux, replace `.\.venv\Scripts\python.exe` in the commands above with `.venv/bin/python`.

Core unit tests do not require Pygame or a graphical display. Integration tests use SDL's dummy video and audio drivers within a limited scope. You can also run the following command to open a window and exit automatically after rendering three frames, checking window creation, drawing, and shutdown:

```powershell
.\.venv\Scripts\python.exe -c "from snake_game.app import run; run(max_frames=3)"
```

Keyboard controls and visual readability still require manual verification in a real game window.
