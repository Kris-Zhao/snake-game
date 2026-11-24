# Feature 05: Woodland UI

## Approval

On 2026-11-24 the user requested a more polished, realistic appearance,
particularly snake colors and background. After viewing two browser mockups,
the user selected **B: Quiet woodland (静谧林地)**. This approves the visual
direction. On 2026-11-24, after reviewing this scope, the user explicitly
approved implementation: “可以开始”. Proceed with developer and independent
tester handoffs without asking for approval again.

## Design

Make the existing desktop game feel like a small woodland scene while keeping
the snake, food, board boundaries, score, and status messages easy to identify.

Approaches considered:

- A: light meadow, olive snake, cream interface. Brighter and simpler visually.
- B: mossy woodland, brown patterned snake, warm neutral interface. More natural
  forest atmosphere; needs stronger contrast between the snake and ground.
  The user selected B.

The selected visual reference is the woodland card in the local brainstorming
mockup `.superpowers/brainstorm/nature-ui/content/nature-styles.html`.

Coordinator proposals for implementation:

- Use subdued moss/soil greens with a lightly textured ground, scattered grass
  and leaves, and a subtle grid. Decorative leaves are not obstacles.
- Draw a connected brown/tan snake with darker markings, rounded bends,
  directional eyes, and a tapered tail. Keep the silhouette distinct from the
  background, including when the snake is long.
- Replace the food dot with a red apple, including a stem, leaf, and highlight.
- Use warm cream/tan score and help areas, clear spacing, and cohesive paused,
  game-over, and victory panels with readable keyboard hints.
- Use procedural Pygame drawing and existing fonts, with no downloaded art or
  new dependencies. These are implementation choices proposed by the coordinator.
- Preserve the current English interface text and default 600 × 724 window.

This is a visual update. Preserve the 20 × 20 default board, 8 simulation ticks
per second, controls, score rules, and lifecycle behavior. Keep core modules and
simulation independent of rendering. No menus, sound, or new game mechanics.

## Implementation scope and acceptance criteria

Primary production file: `src/snake_game/rendering/view.py`. Preserve the
`window_size`, `status_lines`, and `GameView.draw` interfaces. Keep drawing helpers
small and private; cache deterministic terrain by board size using isolated
randomness. No changes to core, input, or scheduling are expected.

1. The board, HUD, footer, and overlays follow the selected woodland palette;
   terrain remains quiet enough to distinguish the play boundary and entities.
2. Brown patterned snake segments connect only to consecutive adjacent segments.
   Head/eyes follow `state.direction`, not pending input. Four directions, bends,
   tapering tails, short snakes, and long snakes render without unintended bridges.
3. A recognizable red apple occupies the food cell; `food=None` draws no apple.
   Decorative details do not suggest an additional occupied cell.
4. Actual score, controls, and running/paused/game-over/won feedback reach the
   visible Surface. The default window remains 600 × 724; a small rectangular
   constructed state draws without negative panel dimensions or clipped messages.
   Supporting this existing state interface does not add board configuration UI.
5. Repeated draws of the same state produce identical pixels and leave game state
   and global randomness unchanged. Imports remain inert; core stays Pygame-free.
6. Existing rule, timing, input, and lifecycle checks pass. Rendering tests check
   meaningful visible regions and text, rather than requiring old colors at a
   single pixel or old fixed text positions.

Implementation sequence after approval:

- [x] Implement terrain, warm HUD/footer, directional patterned snake, and apple.
- [x] Restyle state panels; adapt affected rendering tests in
  `tests/integration/test_view.py` and `test_desktop_verification.py`, adding
  focused woodland rendering checks as needed. Preserve behavioral assertions.
- [x] Run independent tester verification; resolve defects through the developer.
  Save running, paused, game-over, and won screenshots under
  `docs/reports/screenshots/woodland/`, including a long bent snake and full-board
  victory for visual inspection. Record checks and limitations in the report.

Verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit
.\.venv\Scripts\python.exe -m pytest tests/integration
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -c "from snake_game.app import run; run(max_frames=3)"
```

Use the existing scoped SDL dummy fixtures for automated graphical tests.
For the finite native-window check, record the actual driver and result;
it cannot establish physical keyboard operation or sustained responsiveness.

## Verification baseline

Before changes, `.venv/Scripts/python.exe -m pytest -q` completed with
**130 passed in 2.76s** on 2026-11-24. No application code has been modified.

## Delivery workflow

After scope approval, hand this exact plan and approval context to the
`developer` using `$implement-feature`. A separate `tester` using `$test-feature`
will verify the criteria independently and document results in
`docs/reports/05-woodland-ui.md`. Keep test writers sequential. Report any visual
or interactive behavior that could not be checked in a real window.

## User workflow override

During implementation the user explicitly required using only Superpowers
skills. This supersedes the local-skill references in Delivery workflow above.
Earlier planner/developer/tester work used project-local skills alongside
Superpowers; preserve that history and completed work. Remaining verification,
review and fixes use Superpowers skills only. Keep independent role boundaries,
acceptance criteria and approved product scope unchanged.
