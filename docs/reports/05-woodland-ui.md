# Woodland UI independent verification

Date: 2026-11-24. Approved scope: `docs/plans/05-woodland-ui.md`, quiet woodland B, implementation approved with “可以开始”.

Workspace: `C:/Users/zhaoy/.codex/worktrees/woodland-ui/snake-game` (isolated app-managed worktree). Python: `D:/Projects/snake-game/.venv/Scripts/python.exe`, Python 3.12.13, Pygame 2.6.1. Pytest resolves this worktree's `src` through pyproject.toml. Standalone investigation explicitly used this worktree's `src` in PYTHONPATH.

Independent tester edited tests and this report only. No production fixes. Initial handoff used the project test-feature skill; after the user's Superpowers-only override, subsequent work used Superpowers systematic-debugging, receiving-code-review and verification-before-completion. Earlier evidence was retained without restarting.

## Acceptance results

| Criterion | Result | Evidence |
| --- | --- | --- |
| 1. Woodland board, HUD, footer, overlays and entity distinction | Passed | Inspected all four supplied PNGs. Warm neutral interface, subdued green terrain, clear board edge, patterned brown snake and red apple remain distinguishable. Texture/detail tests pass. |
| 2. Consecutive connections, directional head/eyes, bends, taper, short/long snakes | Passed | Independent tests verify actual pupil geometry in four directions, both eyes separated across the head, horizontal/vertical bend seams, foreground gap between nonconsecutive neighboring cells, and tail taper in four orientations at board edges. Existing pending-input invariance test passes. Long bent running and full-400-cell won screenshots inspected. |
| 3. Apple and food=None | Passed | Independent pixel comparison proves apple affects only its food cell at top-left, bottom-right and interior; food=None restores the exact reference. Cell palette/detail checks and screenshot inspection establish red fruit, stem, leaf and highlight. |
| 4. Actual score, controls and feedback visible; default/small rectangles | Passed | Complete font rasters located on actual Surfaces for score3970, title, both control lines, paused/game-over/won titles and hints across 20x20, 4x3, 2x7 and 7x2 states, all statuses. Default remains600x724. Legacy tests retain display-Surface coverage for score170 and all status labels, now independent of fixed coordinates. |
| 5. Identical pixels, state/global RNG preserved, inert imports/core isolation | Passed | Independent deepcopy equality and global random.getstate comparison; repeated render after resizing terrain cache and a fresh renderer produce identical complete RGB bytes. Existing subprocess imports forbid even transient initialization; core runs with site packages disabled and Pygame blocked. |
| 6. Existing rule/time/input/lifecycle behavior; meaningful render checks | Passed | Unit83, integration81, complete164 tests pass. Production diff limited to rendering/view.py. Legacy hardcoded text positions replaced with visible-raster search; redundant min-width420 assertion removed in favor of content checks. |

## Commands and observed results

All commands executed from the isolated workspace above. Each exited0.

```powershell
& D:/Projects/snake-game/.venv/Scripts/python.exe -m pytest tests/unit -q
# 83 passed in 0.24s
& D:/Projects/snake-game/.venv/Scripts/python.exe -m pytest tests/integration -q
# Final bounded test-review run: 81 passed in 9.75s
& D:/Projects/snake-game/.venv/Scripts/python.exe -m pytest -q
# Final bounded test-review run: 164 passed in 9.36s
git diff --check
# No output, exit0
```

Independent new file `tests/integration/test_woodland_verification.py` contributes27 cases: 16 complete-content rectangle/status cases, four directional-eye cases, one consecutive-versus-touching-body case, four taper/edge cases, one food-absence locality case and one resize/cache/state/RNG case. Existing renderer tests remain in the complete suite.

## Investigation and defects

No reproducible production defects found within approved scope.

The initial independent connection test reported26 passed/1 failed because it required exact terrain at a nonconsecutive neighbor seam. Diagnosis: seam RGB was(60,72,46) versus terrain(75,89,57). Suppressing only the translucent entity-shadow color(19,25,14,65) restored the exact terrain pixel; no foreground body bridge existed. The final geometry test explicitly separates decorative shadow from body and verifies that all consecutive seams still connect. No production changes were made for this false-positive expectation.

Review identified brittle legacy tests, resolved in this test-only wave: hardcoded score/overlay positions and a minimum-width assertion unrelated to content visibility. Both were replaced/superseded by complete actual-raster checks; score/status/display coverage was retained.

## Visual evidence and limits

Inspected existing `screenshots/woodland/running.png`, `paused.png`, `game_over.png`, `won.png`. Won image shows the full serpentine board with score3970 and no apple; overlays retain readable foreground text. Screenshot generation itself was developer supplied, not repeated by tester.

Automated adapter tests use scoped SDL dummy video/audio fixtures. Coordinator separately reports a three-frame native-window smoke: source confirmed from the worktree, Windows video driver, running result, Pygame shut down. That native evidence is attributed to coordinator, not an independent tester run.

Physical keyboard operation, prolonged play/responsiveness, and appearance under alternate display scaling remain manual/unverified. They are not established by dummy screenshots, synthetic event tests or the finite native smoke. No environment blockers encountered.

## Coordinator completion evidence

Fresh coordinator full suite: 164 passed in 6.20s, exit0. One PytestCacheWarning
reported a sandbox-denied write to .pytest_cache; test execution and assertions
completed. Independent tester's final run above had no environment blocker.
Coordinator git diff --check exited0. Final code review approved integration;
both test-only findings were closed (see 05-woodland-ui-review.md).

Coordinator native smoke command used explicit worktree PYTHONPATH and the
original Python3.12 venv executable. The source path printed the isolated
worktree renderer; SDL video driver was windows; run(max_frames=3) returned
running, and pygame.get_init() was False afterward. Exit0.

Workflow decisions: implement the tightly coupled rendering changes as one
review unit; use a native isolated worktree after correcting the initial
in-place setup; preserve existing developer/tester role separation while
obeying the later Superpowers-only skill instruction; give constructed small
boards minimum width460 and vertical allocation140 for readable overlays.
The default window and all game rules remain unchanged.
