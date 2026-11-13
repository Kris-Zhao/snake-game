# Feature 03 independent verification

Verified 2026-11-05 against approved `docs/plans/03-pause-and-restart.md`,
`docs/PRD.md`, and `AGENTS.md`, using the test-feature skill. Tester changed
only this report and `tests/unit/test_lifecycle_verification.py`; no production
code was changed.

## Results

| Criterion / approved requirement | Status | Evidence |
| --- | --- | --- |
| AC-01 restart geometry, score, status, direction, pending input, free food | Passed | Existing lifecycle tests cover every source status and default geometry. Independent test compares every resulting field against literal expected state and food selected from independently enumerated free cells. |
| AC-07 pause/resume changes status only; inactive ticks/input inert | Passed | Lifecycle tests exercise all directions and inactive statuses, with and without queued input, repeated ticks and terminal toggles. Independent tests repeat pause/resume five times, preserving queued turns and all state. |
| Pending turn survives pause and applies once on resume; paused inputs are not deferred | Passed | Existing tests cover no pending input and resumed motion. Independent tests preserve both perpendicular turns through repeated cycles, consume the queued turn on a resumed meal, then accept a new turn on the following tick. Resume alone preserves geometry. |
| AC-08 core restart from running, paused, game-over, won | Passed (core scope) | Every source status is tested; independent tests also reach collision and victory through actual ticks, reject terminal resume/input, and successfully restart. Newly requested turns work after restart. |
| Supplied RNG stream continues; no reseeding, global randomness, or inactive selection | Passed | Independent oracle advances two seeded generators before successive restarts and checks exact food choices and generator states. Lifecycle selector checks exactly one selection from default free cells. No-selection doubles and global RNG snapshots cover inactive operations. |
| Old states remain immutable | Passed | Snapshots verify inputs unchanged across lifecycle transitions, restarts, resumed growth and turns; prior immutability tests remain green. |
| AC-10 import/core execution without Pygame/display | Passed (core scope) | `test_core_runs_without_pygame_or_site_packages` passes in a Python `-S` child process with Pygame imports explicitly blocked, exercising pause/resume/restart. Source review finds standard-library-only core imports and no import-time application start. |
| AC-11 explicit simulation ticks and supplied randomness | Passed (core scope) | Source review finds no clocks or scheduler in the core. Commands do not move the snake; inactive ticks do not advance it. |
| AC-12 deterministic headless tests and prior regressions | Passed | All 59 unit/full-suite tests pass. |

## Commands and results

Environment: Windows, Python 3.12.13, pytest 9.2.0. Commands run from repository
root with the existing virtual environment. No installation or configuration
changes were needed.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_lifecycle.py tests/unit/test_lifecycle_verification.py
# 21 passed, exit 0
.\.venv\Scripts\python.exe -m pytest tests/unit
# 59 passed, exit 0
.\.venv\Scripts\python.exe -m pytest
# 59 passed, exit 0
```

Independent additions comprise five collected tests covering two queued-turn
directions, one repeated restart/RNG oracle scenario, and two naturally reached
terminal-state scenarios. All fixtures are deterministic and use no sleeps,
wall-clock assertions, Pygame, or display.

## Defects, blockers, and deferred checks

No defects found in the approved Feature 03 scope. No environment blockers.

Actual Space/R/Escape/window-close behavior, scheduler timing reset and absence
of catch-up after pause, and rendered pause/terminal messages remain unverified
and explicitly deferred to Feature 04. Core tests do not establish these
adapter or interactive portions of AC-08, AC-09, or AC-11.
