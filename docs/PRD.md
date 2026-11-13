# Python Snake Game product requirements

Status: requirements baseline for future planning; implementation has not begun.

## Purpose

Build a local, single-player desktop Snake game using Python 3.12 and Pygame.
Keep the rules independently testable with pytest without a graphical window.

## Initial release scope

- A rectangular grid with one snake and one food item while space remains.
- Arrow-key controls, fixed simulation ticks, and responsive window events.
- Growth and score when eating food; wall and body collision end the game.
- Pause/resume, restart, game-over and victory feedback, and clean exit.

Exclude networking, multiplayer, persistent scores, sound, menus, custom art,
packaging installers, and difficulty progression from the initial release.

## Default behavior to use in feature plans

The board is 20 by 20 cells. A new game starts with a three-cell snake near
the center, moving right, score zero, and one food item on an unoccupied cell.
Movement advances at 8 ticks per second, independently of rendering frequency.
Each food adds one body cell and 10 points. Walls are solid; there is no wrap.
Only one direction change is accepted per simulation tick. Ignore a direct
reversal and ignore further turns until the next tick. Ignore direction input
while paused or after a terminal state. Space toggles pause; R restarts from
any state; Escape and the window close event exit. A restart resets timing and
pending input as well as game state. Cosmetic choices can be made during
implementation without changing these rules.

## Acceptance criteria

| ID | Observable requirement |
| --- | --- |
| AC-01 | Creating or restarting a game produces an in-bounds, contiguous three-cell snake facing right, score zero, running state, and food outside the snake. |
| AC-02 | Each running tick moves the head exactly one cell in its direction and removes the tail unless food is eaten; length is unchanged on an ordinary tick. |
| AC-03 | A valid arrow-key turn applies on the next tick. Reversal is ignored. Multiple turns before a tick cannot cause a reversal or multiple moves. |
| AC-04 | Eating food grows the snake by one cell, adds exactly 10 points, and generates one new food item uniformly from free cells. Seeded randomness makes scenarios reproducible. |
| AC-05 | Crossing a board edge or entering an occupied body cell ends the game. Entering the tail cell vacated on that same non-growing tick is legal. |
| AC-06 | When the snake fills the board, the state becomes won, food is absent, and food selection terminates without retry loops. |
| AC-07 | Paused, game-over, and won states do not advance movement, food, or score. Space resumes only a paused running game; terminal states require restart. |
| AC-08 | R resets the game from running, paused, game-over, or won. Escape and closing the window shut down cleanly from any state. |
| AC-09 | The Pygame view draws the board, distinguishable snake and food, score, and pause/game-over/won messages matching core state. |
| AC-10 | Core modules import and run with no Pygame installation and no display. Importing any module does not open a window or start an event loop. |
| AC-11 | Core behavior depends on explicit ticks and supplied randomness, not frame rate or wall-clock time. Pausing/resuming causes no accumulated catch-up movement. |
| AC-12 | pytest verifies initialization, movement, turn input, growth, scoring, food placement, collisions, tail-vacating behavior, full-board victory, pause, and restart without a graphical window. |

Use constructed near-full and collision states to verify edge cases; tests need
not play a complete game to reach them. Rendering and interactive controls also
require adapter or manual smoke verification; core tests alone do not prove
those acceptance criteria.

## Architecture requirements

Keep state and rule transitions under `src/snake_game/core/`, using only the
standard library. Define a small state-and-command interface during planning.
The Pygame adapter translates input into commands, schedules ticks, and renders
the resulting state. It must not duplicate rule decisions. Inject a random
generator or food-selection dependency; never hide global random state in tests.

Use `tests/unit/` for rule coverage and `tests/integration/` for adapter checks.
Core tests must work when Pygame is not installed, even though the complete
desktop application declares it as a runtime dependency.

## Delivery workflow

Plan a feature, record user approval, implement the agreed scope, then verify
independently against the relevant acceptance criteria. Plans belong in
`docs/plans/`; verification reports belong in `docs/reports/`. Record defects,
reproduction steps, and blocked or manual checks rather than marking untested
criteria as passed.

The present scaffolding task delivers documentation, dependency metadata,
directories, Codex agent configuration, and reusable skills only. It does not
authorize gameplay implementation or create an approved feature plan.
