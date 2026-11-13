# Snake Game contributor instructions

## Scope and stack

This repository is a scaffold only. Do not implement gameplay until the user
requests a feature and approves its implementation plan. `docs/PRD.md` defines
the intended product and acceptance criteria; none are implemented yet.

Use Python 3.12, Pygame for presentation, and pytest for testing. Dependency
declarations live in `pyproject.toml`.

## Architecture

- `src/snake_game/core/`: game state, movement, collisions, food, and scoring.
  Use only the Python standard library here. Never import Pygame, create a
  window, read keyboard state, or depend on wall-clock time in this layer.
- `src/snake_game/rendering/`: future Pygame drawing and input adapters.
- `src/snake_game/`: future application composition and event loop.
- `tests/unit/`: deterministic core tests that run without Pygame or a display.
- `tests/integration/`: adapter tests; keep graphical smoke checks separate
  from core unit tests.
- `docs/plans/` and `docs/reports/`: future approved plans and verification reports.

Pass directions and explicit simulation ticks into the core. Inject randomness
or supply a seeded random generator for reproducible food placement. The
rendering layer consumes state; it must not own movement or collision rules.
Imports must not initialize Pygame or start the application.

## Role workflow

1. Use `planner` with `$plan-feature` to analyze the request and PRD, identify
   affected boundaries, and return a plan with acceptance criteria and tests.
   The planner does not edit application code, tests, or configuration.
2. Record the plan and the user's approval in `docs/plans/<feature>.md` via the
   coordinating agent. Approval already given in the conversation counts; do
   not ask for it again. A generated plan alone is not approval.
3. Use `developer` with `$implement-feature` to implement the approved scope.
   Hand the developer the exact plan path and approval context.
4. Use a separate `tester` with `$test-feature` to independently derive checks
   from acceptance criteria, add tests, and report defects. The tester may
   edit tests and reports but must not fix production code or weaken criteria.
5. Return defects to the developer and repeat relevant verification until
   resolved, or clearly report remaining defects and blocked checks.

The coordinator owns plan approval, role handoffs, and the final report. Keep
writers on the same files sequential. These reusable roles are configured in
`.codex/agents/` and skills are discovered from `.agents/skills/`. Agent role
boundaries are instructions; agents inherit the session's permissions.

## Setup and verification

After installing Python 3.12, run from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest tests/unit
.\.venv\Scripts\python.exe -m pytest
```

On other platforms use `python3.12 -m venv .venv` and `.venv/bin/python`.
There are intentionally no executable modules or tests yet. Pytest exits with
code 5 when no tests are collected; do not describe that as a passing suite.
For future Pygame adapter checks, use SDL's dummy video/audio drivers when
appropriate, and report which interactive behaviors still need a real window.

## Completion evidence

Tie changes and tests to the approved acceptance criteria. Report commands,
results, and unverified behavior honestly. Keep test fixtures deterministic;
avoid sleeps, machine-specific paths, and GUI dependencies in unit tests.

## Codex configuration references

This setup uses standalone custom-agent TOML files and `[agents]` settings
from the current official documentation, checked on 2026-11-05:

- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/config-file/config-reference
- https://learn.chatgpt.com/docs/config-schema.json
- https://learn.chatgpt.com/docs/build-skills

Project configuration requires a trusted project. Trust is a user-level
setting; this repository does not grant itself trust. Reload/start a new
Codex session after creating these files if the agents are not yet listed.
