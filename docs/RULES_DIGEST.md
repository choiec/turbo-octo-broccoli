---
title: summary
description: Agent-context digest of always-applied rules (§C, §I, §O, §W). Canonical text in docs/RULES.md.
---

# Rule digest (agent context)

This file gives the **always-applied** rule text so the agent has it
in context.\
**Canonical source**: `docs/RULES.md`. Sync this digest when those
sections change.

---

## §C. Language

Language: English only for code, comments, docstrings, UI/log strings,
docs.

---

## §I. Agent principles

Conventions: follow existing formatting, naming, and structure. KISS:
prefer the simplest option; reduce complexity. No speculative
implementation: do not add modules, endpoints, or infrastructure for a
future phase; add only when the feature is in the current todo
(`docs/TODO.md`). Boy scout rule: leave anything you touch cleaner
than you found it. Root cause: find it; address causes, not only
symptoms. Consistency: be consistent across the project (terms, tone,
layout).

---

## §O. Answer format

When a reply presents multiple options or alternatives, list at least
one pro and one con for each option. Keep each pro/con to one short
line unless context requires more. Omit only when options are trivial
or the user asks for no comparison.

---

## §W. Task completion

When finishing code changes, run `ruff format .` and `pytest`; fix any
failures before considering the task complete. If the change touches
DB-dependent code, run `pytest` with `DATABASE_URL` and `NEO4J_*` set
as well.

---

## Which § apply (task type)

| Task type | Sections |
| --- | --- |
| Always | §C, §I, §O, §W |
| Feature / new code | §C, §I, §W + RULES.md §4 (coding), §5 (commit) |
| Refactor | §C, §I, §W + RULES.md §4 (coding), §5 (commit) |
| Docs | §C, §I + RULES.md §2 (naming) |
| Commit | §C + RULES.md §5 (commit), §6 (git) |
| Directory change | §C, §I + RULES.md §2 (structure and naming) |
| Dependency | §C, §I + RULES.md §4 (dependencies) |
| DB / migration | §C, §I, §W + RULES.md §4 (models), §3 (test) |

Read `docs/RULES.md` for full rule text. Read `docs/TODO.md` before
adding any module, route, or infrastructure.
