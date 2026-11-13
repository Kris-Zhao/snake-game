# Feature 01: Initialization, movement, and turn requests

## Approval
User requested the full PRD implementation and explicitly instructed: “Once the plan is ready, spawn the developer subagent to implement the feature using the implement-feature skill.” This authorizes the sequential plan-to-development handoff. Coordinator reviewed the planner's returned plan and records that advance authorization here on 2026-11-05.

## Scope and interface
Implement AC-01 creation, AC-02 ordinary movement, and AC-03 turn queuing. Default board is 20x20, three contiguous cells near center facing right, score zero, RUNNING, one food outside snake.
Standard-library-only immutable GameState dataclass: dimensions, head-first snake tuple, committed direction, pending direction, food, score, status. Direction enum has four grid deltas; GameStatus has RUNNING, PAUSED, GAME_OVER, WON. Public API: new_game(rng), request_direction(state, direction), tick(state, rng). Explicit supplied random.Random-compatible generator; initial food chosen with rng.choice over row-major free cells.
Same-direction and reversal requests are no-ops and do not consume allowance. First valid turn queues until next tick; further turns are ignored. Tick commits pending direction, moves exactly one cell, removes tail, and clears pending input.

## Boundaries and files
Use inert src/snake_game/__init__.py and core public exports, core/model.py and core/engine.py (equivalent small organization permitted). Add tests/unit/test_initialization.py, test_movement.py, test_turns.py, test_core_isolation.py. No Pygame, clocks, keyboard polling, hidden global random state, or import side effects in core. No dependency changes needed.

## Acceptance and tests
- AC-01 creation: default dimensions, distinct in-bounds contiguous length-three snake facing right, zero score, RUNNING, in-bounds unoccupied food; equal seeds reproduce food; selector receives precisely free cells.
- AC-02 ordinary in-bounds non-food ticks: exactly one-cell head movement, prior head second, tail removed, length/score/food unchanged; commands do not move; repeated ticks each advance once.
- AC-03: perpendicular turns apply next tick; reversal ignored; reversal or same direction then valid turn accepted; first valid turn wins; cannot reverse through multiple requests; allowance resets after tick.
- AC-10–12: no display/Pygame dependency; subprocess blocking Pygame imports can exercise core; inert imports; explicit ticks and randomness.
Run .venv/Scripts/python.exe -m pytest tests/unit. Independent tester derives checks and writes docs/reports/01-movement-and-turns.md; edits only tests/reports.

## Deferred scope and risks
Food consumption, collision, victory are feature02; pause/restart/terminal guards feature03; Pygame application feature04. Feature01 is an intermediate core increment. AC-01 restart and AC-02 growing movement remain partial until later features. Tests use in-bounds non-food moves. No unresolved product decisions.
