# Feature 02: Food, growth, collisions, and victory

## Approval
Coordinator reviewed planner's returned plan. User's 2026-11-05 instruction “Once the plan is ready, spawn the developer subagent to implement the feature using the implement-feature skill” authorizes this sequential handoff. Feature01 passed independent verification (20 tests).

## Scope and boundaries
Complete growing AC-02 and AC-04–06. Preserve immutable GameState and new_game(rng), request_direction(state, direction), tick(state, rng). Standard library only, explicit ticks/randomness, no clocks/Pygame/global RNG. Small boards and edge states are constructed directly in tests; no public settings/loading feature needed.

## Implementation
Update core/engine.py; model/exports only for necessary documentation. Share private food selector: row-major free-cell enumeration and one rng.choice when cells remain, None without choice when full.
Tick: non-RUNNING returns unchanged. Resolve queued direction and proposed head. Detect growth by food equality. Check all four bounds and occupied cells (entire snake for growth; snake[:-1] otherwise). Collision sets GAME_OVER preserving last valid snake, food, score; commits attempted direction and clears pending input. Legal movement prepends head and removes tail unless growing. Growth adds exactly10 points, chooses food from resulting free cells, or sets WON/food=None if full. Ordinary moves preserve score/food and consume no randomness.

## Files and tests
Add tests/unit/test_food_and_growth.py, test_collisions.py, test_victory.py. Existing fixtures may be corrected only if they inadvertently enter newly implemented branches; retain intended assertions. No dependencies added.
- Growing AC-02: moves one cell, retains old tail, increases length exactly one.
- AC-04: adds exactly10 to prior score, one free in-bounds replacement food while space exists; recording selector receives precisely row-major free cells once; equal seeds/commands reproduce states; ordinary/collision ticks and global RNG unchanged.
- AC-05: four walls, body entry, queued-turn collision; vacating tail legal; collisions preserve valid geometry/score/food; subsequent ticks inert without RNG.
- AC-06: valid near-full board eats final food, grows once, gains10, WON/no food; raising selector proves no choice on full board. Exactly-one-free-cell case selects it; subsequent won ticks inert.
- Prior tests and Pygame-blocked core isolation remain passing; immutable inputs preserved.
Run .venv/Scripts/python.exe -m pytest tests/unit and -m pytest. Independent tester edits only tests/reports and writes docs/reports/02-food-collisions-and-victory.md.

## Deferred and risks
Full pause/resume, inactive direction guards, restart feature03; adapter feature04. Use contiguous valid constructed snakes; malformed injected-state behavior is outside product contract. No unresolved decisions.
