# Feature 04: Pygame desktop application

## Approval
Coordinator reviewed planner's returned plan. User's 2026-11-05 instruction to proceed from each ready plan to developer authorizes handoff. Features01–03 independently passed; baseline59 tests.

## Scope / files / boundaries
Complete adapter AC-03, AC-08–11 and full desktop game: arrows, Space, R, Escape/window close; fixed8Hz independent rendering; responsive events in every state; reset timing on pause/resume/restart; matching board/score/status rendering; clean exit; executable entry and README. No excluded features/new dependencies.
Suggested application.py (Pygame-free session/controller), rendering/{__init__,input,view}.py, app.py (explicit Pygame lifetime), __main__.py (guarded entry), README.md; tests/unit/test_application_timing.py, integration/test_input.py, test_view.py, test_app.py. Equivalent small organization allowed. Core unchanged except separately justified correction; adapter calls core commands, never duplicates rules.

## Controller and event semantics
Session owns immutable core state, supplied RNG, accumulator, exit flag. Frame/update accepts explicit elapsed time and ordered commands. Prefer integer milliseconds,125ms interval, independent60FPS rendering cap.
Poll events before simulation. Arrows call request_direction; Space toggle_pause; R restart; Escape/QUIT exit immediately. On effective pause/resume or restart, clear accumulator and discard current frame elapsed, preserving discard flag across entire frame even for Space→Space. Inactive states accumulate no time. Otherwise add elapsed, tick once per125ms, preserve remainder; terminal tick clears accumulator and stops. Exit stops without further simulation/drawing. Restart clears earlier arrows; later arrows are fresh input. Transition elapsed never moves newly resumed/restarted state; require fresh125ms.

## Rendering / execution
Draw board sized by dimensions, distinguishable head/body and food, readable score/control help, pause/resume guidance, game-over/restart, victory/restart. Use primitives/default fonts. Shared state-to-text or inspectable actual drawing boundary. No mutation/RNG/ticks in view.
Support .venv/Scripts/python.exe -m snake_game. All imports including __main__ inert. Initialize Pygame/display/fonts/Clock inside run(); try/finally includes initialization and loop, always pygame.quit() on normal/error exit and propagate unexpected errors. Provide finite programmatic run(max_frames=3) seam for smoke (normal interactive run unlimited). Tests can monkeypatch events/clock/draw without large framework.

## Acceptance / verification
- Input AC-03/07/08: each arrow correct and respects core reversal/one-turn limit; Space toggles/inert terminal; R resets all4 states/pending input; Escape/QUIT exit all4 states. Mixed ordered batches: arrow→restart, restart→arrow, pause→arrow, pause→resume, restart→pause, exit then other events.
- Timing AC-11:124+1ms one tick,375ms three ticks, equal elapsed across frame partitions same state, remainder retained; long paused duration no debt; pause/resume clears previous fraction/discards transition elapsed including double toggle; restart same; full fresh interval after reset; terminal remains responsive and accumulates no time.
- View AC-09: SDL dummy real Surface/display for all4 statuses; dimensions, distinguishable snake/food, actual score/messages, won without food, state preserved.
- Imports AC-10: retain core Pygame-blocking execution; subprocess imports every module including __main__ with Pygame installed, asserts no Pygame/display init/loop.
- Lifetime: dummy finite run initializes/draws/closes; injected QUIT/Escape clean; initialization/render failure still quits; deterministic no sleeps/GUI dependency.
Preserve all prior tests. Run .venv/Scripts/python.exe -m pytest tests/unit, tests/integration, then full pytest. SDL dummy env only scoped tests/subprocess, restore afterward. Tester independently derives checks, edits only tests/report docs/reports/04-pygame-application.md.

## Delivery
README Python3.12 venv/install/module launch, controls/default rules/testing. After independent pass coordinator runs full suite and finite real-driver launch when supported; record driver/creation/draw/shutdown. Finite launch does not establish physical keyboard operation/readability/prolonged responsiveness. Report unperformed checks honestly. Cosmetics unrestricted. No unresolved decisions.
