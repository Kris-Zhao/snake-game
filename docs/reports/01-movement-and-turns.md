# Feature 01 independent verification

Date: 2026-11-05. Scope: approved `docs/plans/01-movement-and-turns.md`.
Expected behavior was derived from the approved plan and PRD before comparing
implementation and existing tests. Production code was not modified.

## Results

| Criterion | Result | Evidence and limits |
| --- | --- | --- |
| AC-01 creation | Passed | Default 20x20 board, distinct contiguous three-cell snake near center facing right, RUNNING, zero score, no pending turn, in-bounds free food. Equal seeds reproduce state; selector receives exactly 397 free cells in row-major order. Restart is deferred. |
| AC-02 ordinary movement | Passed | All four directions move one cell with previous head second and old tail removed; length, score, food preserved. Repeated explicit ticks advance once each. Food consumption is deferred. |
| AC-03 core turn commands | Passed | Commands preserve position and committed direction until tick. All 256 three-request sequences (64 for each starting direction) respect the first perpendicular turn, ignore same-direction/reversal without consuming allowance, and move once. Pending input clears; opposite direction remains rejected after commitment; another valid turn is accepted after the tick. Arrow-key translation is deferred. |
| AC-10 core isolation | Passed for current modules | Subprocess uses Python `-S` with a Pygame import blocker and exercises creation, turn, tick. Package imports are inert; source review finds standard-library imports only and no window/event loop. Future adapter imports remain unverified. |
| AC-11 explicit ticks/randomness | Passed for current core | No clock or keyboard access in current core. Injected duck-typed selector controls initial food; ordinary ticks do not call it; creation/commands/ticks leave global random state unchanged. Pause timing/catch-up is deferred. |
| AC-12 relevant tests | Passed for Feature 01 subset | Deterministic initialization, ordinary movement, turn, immutable-state and isolation tests pass without graphical setup. Remaining PRD cases are deferred. |
| AC-04–09 and remaining AC-01/02/10–12 behavior | Unverified/deferred | Growth, scoring changes, collisions, full board, pause/restart, terminal guards, Pygame presentation/input/exit and timing are outside this increment. Full PRD acceptance is not claimed. |

## Commands and evidence

Environment: Windows, Python 3.12.13, pytest 9.2.0, repository root.

- Baseline `.\.venv\Scripts\python.exe -m pytest tests/unit`: 14 passed, exit 0.
- After independent checks `.\.venv\Scripts\python.exe -m pytest tests/unit`:
  20 passed in 0.24s, exit 0.
- `.\.venv\Scripts\python.exe -m pytest`: 20 passed in 0.21s, exit 0.
- `rg -n "^(import|from)|^def |^class " src/snake_game`: confirms current
  imports are standard library or local core modules; source inspection also
  checked inert package initialization and absence of clock/display access.

Added `tests/unit/test_movement_verification.py` with six collected cases:
four starting-direction cases, each exercising 64 request sequences; injected
randomness/global-state isolation; immutable state and preserved input.
Literal movement deltas in these checks are independent of the implementation's
`Direction.delta` property.

## Defects, blockers, and manual checks

No defects found within the approved Feature 01 scope. No test environment
blockers. `git status --short` cannot report changes because this workspace
has no Git repository; this does not block runtime verification.

No graphical checks were performed or required for this core-only increment.
Future application verification must cover real keyboard/window input,
rendering, responsiveness, pause timing and clean exit. Deferred rules must
receive independent verification in their respective feature increments.
