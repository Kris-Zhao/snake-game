---
name: implement-feature
description: Implement a feature from an approved plan, add relevant tests, and report verification evidence.
---

# Implementation workflow

1. Read `AGENTS.md`, `docs/PRD.md`, and the approved plan supplied at handoff.
2. Confirm that the requested scope is authorized; existing approval counts.
   Return missing approval to the coordinating agent before application changes.
3. Implement the assigned scope while respecting project architecture.
4. Add appropriate tests and run focused checks and affected existing tests.
5. Report changed files, acceptance-criterion coverage, commands, results, and
   remaining limitations to the coordinating agent.

Raise material scope or behavior changes with the coordinating agent before
implementing them. Do not relax acceptance criteria to make checks pass.
Developer self-checks do not replace independent verification.
