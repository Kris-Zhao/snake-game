# Woodland UI whole-change review

## Verdict

Approved for integration. The implementation meets the approved design and acceptance criteria. Both test findings are resolved, with no outstanding review findings.

Reviewed the worktree changes against baseline be97454b7403f0858bdc452396a990227c2dfef3 and docs/plans/05-woodland-ui.md, including both new rendering-test files. Inspected the running and full-board victory images.

## Initial findings (resolved)

1. **Important — position-dependent text test (AC6).** At tests/integration/test_desktop_verification.py lines 106–116 the test requires an exact score origin and reproduces the panel dimensions and text offsets. In a read-only experiment the score moved down one pixel. The legacy assertion failed, although the complete score raster was visible on the SDL display Surface and the independent raster search found it. Use a shared position-independent raster assertion for this test. Retain the original score, labels, hints and actual display-surface coverage.
2. **Minor — unsupported minimum width.** At tests/integration/test_woodland_view.py line 70 the small-board test requires a window at least 420 pixels wide. Only default dimensions are contractual. On a 400-pixel-wide Surface, the 4 × 3 fixture showed the complete title, score, controls and applicable status text in all four states. Remove the arbitrary bound and keep the independent checks for text fit.

## Acceptance evidence

- Terrain uses isolated seeded randomness and caches the most recent board dimensions. The renderer reads the core state. Input, scheduling, dependency declarations and core files have no changes.
- Consecutive Manhattan-adjacent cells establish the links. The head rotates using current direction, the terminal polygon tapers toward its tip, and the apple's details fit its cell. The screenshots show discernible entities and a traceable full-board path.
- The default geometry yields 600 × 724. The overlay uses the available small-window space. Independent tests cover visible hints and score on narrow and shallow boards, geometry in four directions, removal of the apple, reproducible pixels across resize, and RNG/state preservation.
- Reviewed the reported 137-test developer run and the coordinator's three-frame native Windows smoke result. The reviewer performed focused SDL dummy-surface experiments. Physical keyboard behavior and sustained native responsiveness were outside this review.

## Scoped re-review

- The desktop test still creates a display Surface with pygame.display.set_mode and renders the real GameView. It searches for candidate glyph rows and compares each entire in-bounds text raster. It asserts the score and both applicable overlay lines, with no expected coordinates.
- The 4 × 3 smoke test has no arbitrary width bound. The independent content assertions still cover every status across four board shapes.
- These test-only fixes close both findings. The tester's final report records 83 unit tests passed, 81 integration tests passed and 164 passed in the complete suite. This scoped re-review inspected the changed assertions without rerunning the suite.
