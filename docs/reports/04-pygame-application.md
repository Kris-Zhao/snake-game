# Feature 04 independent verification

Verified 2026-11-05 against `docs/PRD.md` and approved
`docs/plans/04-pygame-application.md`. Tester read AGENTS.md and used
`.agents/skills/test-feature/SKILL.md`. Production code was not changed.

## Results

Python 3.12.13, pytest 9.2.0, Windows. Integration fixtures scope SDL dummy
video/audio drivers to each test and restore the environment afterward.

| Command from repository root | Result |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest tests/unit` | 83 passed, 0.35 s |
| `.venv/Scripts/python.exe -m pytest tests/integration` | 47 passed, 2.49 s |
| `.venv/Scripts/python.exe -m pytest` | 130 passed, 2.68 s |

The final full run includes a test-only cleanup after the separate runs:
explicit key-code mapping and an injected clock in additional failure checks.
No criteria or expected behavior were weakened. The first development run of
new tests found five test-harness errors from incorrectly cased Pygame key
constants; these were corrected. They were not application defects.

Added 10 independently derived unit cases in
`tests/unit/test_application_verification.py` and 22 integration cases in
`tests/integration/test_desktop_verification.py`. Existing 98 cases remain.

## Acceptance evidence

| Criterion | Status | Evidence |
| --- | --- | --- |
| AC-03 arrow adapter and turn discipline | Passed automatically | Each arrow's command mapping; rejection of reversal and extra turns; mixed real-loop arrow/restart ordering. Paused arrows are ignored, post-resume arrows accepted, and a second turn remains rejected. Existing core turn tests remain passing. |
| AC-07 inactive-state behavior (regression) | Passed automatically | Paused, game-over and won sessions preserve complete state and RNG through short and very long frames and arrows. Terminal Space is inert. Pause/resume and double-toggle clear timing. Existing core lifecycle tests pass. |
| AC-08 restart and clean exit | Passed automatically | Restart from all four states clears score, pending input and timing, restores right-facing initial snake and valid food, and requires a fresh 125 ms. Actual event-loop QUIT and Escape each exit every status before simulation/drawing, ignore subsequent restart, and release display/Pygame. |
| AC-09 actual rendered content | Passed with dummy-driver scope | Real SDL Surfaces/displays for all four statuses. Existing tests check actual head/body/food pixel colors and state preservation. New tests compare actual score and overlay text pixels with expected rasterized score, pause/resume, game-over/restart and victory/restart text. Won rendering safely handles absent food. Default window is 600 by 724. Human readability remains manual. |
| AC-10 import and core isolation | Passed automatically | Existing subprocess runs core using `-S` and a Pygame-blocking import finder. Both existing and new subprocess tests discover/import every application module including `__main__`. New test replaces Pygame init/display/font/Clock/event entry points with failing sentinels, preventing even transient initialization or event-loop entry. |
| AC-11 fixed simulation timing | Passed automatically | 124+1 ms boundary, 375 ms/three ticks, preserved remainder, equal elapsed partitions, identical RNG evolution through growth. Long pause creates no debt. Reset/double-toggle transition frames discard elapsed; real-loop frames of 10000,124,1 ms verify fresh interval. Wall collision and full-board win stop catch-up and clear accumulator. |
| AC-01/02/04/05/06/12 prior core coverage | Passed regression | All prior initialization, movement, food/growth/scoring/randomness, collision/tail-vacating, victory and lifecycle cases remain passing; unit suite runs without display use. |
| Runtime lifetime and failure cleanup | Passed automatically | Finite dummy run draws/flips three frames and quits. Injected initialization, display creation, rendering, font construction, clock construction, event polling and flip errors propagate while releasing Pygame/display resources. |

Mixed batches cover arrow→restart, restart→arrow, pause→arrow,
pause→resume→arrow, restart→pause and exit→restart. New real-loop tests use
explicit elapsed values and preserve actual drawing, rather than replacing
the entire application with mocks. Timing fixtures use no sleeps.

## Defects and remaining checks

No reproducible production defects found. No automated checks blocked.

The tester did not perform a real-driver launch or interactive desktop review.
Coordinator owns that follow-up after this handoff. SDL dummy checks do not
establish physical arrow/Space/R/Escape input, visible window-close operation,
readability, scaling, focus behavior, or prolonged responsiveness in a real
window. A finite real-driver smoke alone will not establish all those behaviors.

Repository has no `.git` directory, so Git status/diff was unavailable; changes
were limited to the two new test files and this report.
