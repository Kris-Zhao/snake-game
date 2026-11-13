---
name: test-feature
description: Independently verify a feature against acceptance criteria, add tests, and report reproducible defects.
---

# Testing workflow

1. Read `AGENTS.md`, `docs/PRD.md`, the approved plan, and relevant implementation.
2. Derive expected behavior from acceptance criteria; do not assume the
   implementation or developer tests are correct.
3. Identify normal paths, boundary conditions, and invalid state transitions.
4. Add missing tests using the project's test framework and run relevant checks.
5. Report each criterion as passed, failed, or unverified, with commands and evidence.
6. Report defects with severity, file references, reproduction steps, and expected
   versus actual behavior. Separate environment blockers and manual checks.

Edit only tests and verification reports in `docs/reports/`. Do not fix
production code or weaken requirements or assertions to obtain a pass.
Return findings to the coordinating agent for developer follow-up.
