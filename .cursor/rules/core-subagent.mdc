---
description: |
  When you run or configure parallel subagents (e.g. Task tool). Domain
  partition and commit-only-touched-files; subagents respect boundaries.
alwaysApply: false
---

**§SA (Subagent partition)**: When running parallel subagents, assign work by
domain directory. Each subagent may only modify files under its assigned domain
(e.g. `app/routers/`, `app/models/`, `tests/`). Do not touch shared files —
`main.py`, `pyproject.toml`, root-level config — leave those for the main agent
to aggregate.

**§SB (Subagent commit)**: When a subagent finishes, it must run `git add` on
only the files it modified, then `git commit`, unless the main agent explicitly
forbids committing. Use the project commit message format:
`<type>: <description>`; imperative, lowercase.
