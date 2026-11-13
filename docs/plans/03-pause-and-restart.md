# Feature 03: Core pause/resume, restart, inactive input guards

## Approval
Coordinator reviewed planner's returned plan. User's 2026-11-05 explicit instruction to spawn developer once plan is ready authorizes this sequential handoff. Features01–02 passed independent verification; baseline38 tests.

## Scope and interface
Complete core AC-01 restart, AC-07, restart part of AC-08. Add toggle_pause(state) and restart(state,rng) to core/engine.py and public exports. Keep immutable schema and prior rules. No dependencies/config changes.
toggle_pause changes only RUNNING to PAUSED or PAUSED to RUNNING; terminal states ignore it. Preserve an already accepted pending turn through pause/resume. request_direction returns unchanged unless RUNNING; ignored paused inputs must not appear after resume. Keep inactive tick guard. restart delegates new_game(rng) from any state, resetting default geometry, status, score, direction, food, and pending input; supplied RNG continues its stream without reseeding/global state.

## Implementation and tests
Add RUNNING direction guard, status-only toggle, restart, exports/docstrings, then tests/unit/test_lifecycle.py and update Pygame-blocked core isolation exercise if needed.
- AC-07: toggle preserves all fields except status; terminal toggles inert; repeated inactive ticks and all four directions ignored for PAUSED/GAME_OVER/WON, with/without pending turn. Paused input never deferred; accepted prior turn survives and applies once next running tick. Resume itself never moves. No RNG consumed by inactive commands/ticks/toggles.
- AC-01/08: restart from each status with altered geometry/direction/score/pending input produces default20x20 contiguous three-cell center snake RIGHT, no pending, score0 RUNNING and free food. Seeded fresh generators reproduce results; recording selector receives default free cells once. Old state immutable; next tick moves right unless new turn supplied. Existing RNG stream is preserved.
- AC-10–12: new commands work with Pygame blocked/no display, no clocks/global RNG/import side effects; all prior tests pass.
Run .venv/Scripts/python.exe -m pytest tests/unit/test_lifecycle.py, -m pytest tests/unit, and -m pytest. Tester derives independent checks, owns only tests/reports, records docs/reports/03-pause-and-restart.md.

## Deferred and risks
Actual Space/R/Escape/window events and scheduler reset/catch-up AC-08/11 feature04. Preserve already accepted pending turn on pause consistently; restart explicitly clears. No unresolved decisions.
