# Feature 02 independent verification

Date: 2026-11-05. Approved scope: `docs/plans/02-food-collisions-and-victory.md`.
Tester used `.agents/skills/test-feature/SKILL.md`, reviewed AGENTS.md, PRD,
approved plan, implementation, and existing tests. Only tests and this report
were edited during independent verification.

## Results

| Criterion | Status | Evidence and scope |
| --- | --- | --- |
| AC-02 | Passed | Ordinary ticks retain length; eating prepends exactly one neighboring head and retains the old tail. Independent exhaustive compact-board checks cover legal transitions and input immutability. |
| AC-04 | Passed | Growth adds exactly 10 to a nonzero prior score. Recording selectors receive all and only free cells, without duplicates, once per nonfinal meal. Existing checks verify row-major order and equal-seed reproduction. Production delegates selection to supplied `Random.choice`, providing uniform selection over the enumerated cells. Ordinary and collision ticks consume no randomness; global random state stays unchanged. |
| AC-05 | Passed | All four wall boundaries, occupied-body entry, queued-turn collision, and legal vacating-tail movement are covered. Failed moves preserve snake, food, and score, commit the attempted direction, clear pending input, and become terminal. |
| AC-06 | Passed | Constructed final meals and a three-meal sequence fill the board, add exactly one cell and 10 points on each meal, enter WON, and remove food. Selectors forbid selection on a full board; subsequent terminal ticks remain inert. A one-free-cell replacement case also passes. |
| Prior feature regression | Passed | Initialization, ordinary movement, first-valid-turn handling, reversal rejection, and immutable state tests remain passing. |
| AC-07 terminal/nonrunning ticks | Passed for tick behavior | Paused, GAME_OVER, and WON tick calls preserve state and avoid randomness. Pause/resume commands and inactive direction guards are deferred to feature 03. |
| AC-10 / AC-11 core boundary | Passed for implemented core | Existing subprocess check blocks Pygame imports and disables site packages; core imports and explicit tick/turn execution succeed. Core source uses standard-library dependencies and supplied randomness, with no clock or display dependency. Adapter timing and import coverage for future application modules remain deferred. |
| AC-12 | Passed for feature 02 scope | Headless pytest covers implemented initialization, movement, input, growth, scoring, food, collisions, tail-vacating, and victory. Full pause/restart coverage awaits feature 03. |

Added `tests/unit/test_food_collision_verification.py` with four collected tests:
three exhaustive checks enumerate every contiguous, distinct-cell snake of
length 3, 4, or 5 on a 3-by-2 board, every nonreversing turn, and every valid
food position. They independently check movement geometry, collision snapshots,
tail-vacating, score, food eligibility, random-call counts, terminal invariance,
and immutable inputs. The fourth check follows consecutive meals and turns to
victory, then attempts ten more ticks without advancing the game.

## Commands and environment

Windows, Python 3.12.13, pytest 9.2.0, repository-local virtual environment.
Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit
# 38 passed, exit 0
.\.venv\Scripts\python.exe -m pytest
# 38 passed, exit 0
```

No graphical window, sleeps, network access, or nondeterministic statistical
sampling was needed. Uniformity is checked structurally through unique complete
candidate lists and use of standard-library `Random.choice`, rather than a
flaky frequency threshold.

## Defects and deferred checks

No production defects found in the approved feature 02 scope. No environment
blockers prevented verification.

AC-01 restart, full AC-07 pause/resume and inactive direction-input handling,
and AC-08 restart/exit remain deferred to subsequent features. AC-09 rendering,
arrow/Space/R/Escape handling, window-close behavior, and rendering-independent
timing require future adapter tests and real-window smoke verification. This
report does not mark those unimplemented behaviors as passed.

Malformed manually injected states are outside the approved contract and were
not used to establish correctness. No production changes were made by tester.
