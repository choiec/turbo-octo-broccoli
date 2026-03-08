---
title: ruleset
description: Single source of truth for project conventions, structure, and workflow.
---

# Project rules (AI / tooling)

Single source of truth for project conventions, structure, and
workflow.\
All tools and agents use this file only; do not duplicate these rules
in tool-specific configs.\
Canonical text for always-applied rules (§C, §I, §O, §W) is here;
`docs/RULES_DIGEST.md` carries the digest for agent context.

---

## 1. Project and stack

- **Name**: learner-portfolio
- **Runtime**: Python 3.14
- **Stack**: FastAPI (HTTP), Pydantic v2 / SQLModel (validation),
  SQLite (relational), FalkorDB (graph)
- **Entry**: `main.py`
- **Type checker**: `ty`; **linter / formatter**: `ruff`
- **Consumers**: Copilot Studio agents via HTTP

---

## 2. Directory structure and naming

- **Max depth**: 5 components from root (root not counted).
- **Naming**: `snake_case` only — lowercase letters and underscores;
  no hyphens, no camelCase in file or directory names.
- **Core files**: named after the technology they wrap (`sqlite.py`,
  `falkordb.py`, `config.py`).
- **Router and model files**: singular domain noun (`grammar.py`,
  `practice.py`); no abbreviations.
- **Exceptions**: `.git`, `.cursor`, `.venv`, `__pycache__`,
  `.pytest_cache`, `.ruff_cache`
- Do not add a sixth path component. Do not use camelCase or hyphens
  in directory or file names.
- **.cursor/ file naming**: Files under `.cursor/rules/`,
  `.cursor/commands/`, and `.cursor/skills/` use
  `<domain>-<topic>` — exactly two lowercase segments separated
  by one hyphen. Allowed domains: `core`, `code`, `data`. No
  single-word names; no three-or-more-segment names.

---

## 3. Run, build, test

- **Install**: `uv sync`
- **Dev server**: `uvicorn main:app --reload` (SQLite embedded;
  FalkorDB required if using graph features)
- **Test**: `pytest`; storage tests require `SQLITE_PATH` and `FALKORDB_*`
  env vars set.
- **Lint / format**: `ruff check .` / `ruff format .`
- **Type check**: `ty check`; run before considering any task complete.

---

## 4. Coding conventions

- **Language**: English only for code, comments, docstrings, UI/log
  strings, and docs.
- **Line length**: 80 characters maximum (ruff enforced).
- **Type annotations**: All functions must have type annotations —
  parameters and return type. Use `from __future__ import annotations`
  at the top of every file. No `Any` unless unavoidable; prefer
  `TypeAlias` over bare strings.
- **Function length**: Body 2–4 statements. Extract helpers rather than
  growing a function. File ≤100 effective lines (blank lines and
  comments excluded).
- **Imports**: Absolute imports only — no relative `..` imports. Group
  order: stdlib → third-party → local. One blank line between groups.
- **Models**: SQLModel classes in `app/models/<domain>/`. Use `Field()`
  for all columns with explicit `nullable` and `default`. No raw `dict`
  as return type — always use a Pydantic/SQLModel schema.
- **Error handling**: Raise `HTTPException` at the router layer only.
  Domain functions raise plain Python exceptions; routers convert them.
- **Comments**: Intent only. No prose narrating what the code does.
  No `# type: ignore` or `# noqa` unless a comment explains why.
- **Todo**: Do not add modules, routes, or infrastructure unless listed
  in `docs/TODO.md`; update TODO.md first, then implement.
- **Dependencies**: Add only via `uv add`; update `pyproject.toml`
  first; no new deps without a stable-library rationale.
- **Conventions**: Follow existing formatting, naming, and structure;
  prefer the simplest option (KISS); be consistent.

---

## 5. Commit conventions

- **Format**: `<type>[(scope)]: <description>` — imperative, lowercase.
- **Types**: feat, fix, docs, chore, refactor, perf, test, ci, build.
- **Scope**: optional module or domain name (e.g. `english`, `core`).
- **Body**: one blank line after subject; wrap at 72 chars; explain
  *why*, not *what*.
- **No scope creep**: one logical change per commit.

---

## 6. Git strategy

- **Trunk-based**: work directly on `main`. No long-lived feature
  branches.
- **Experiment exception**: short-lived `exp/<topic>` branches for
  risky exploration; local only; merge or delete within the same
  session.
- **No PR workflow**: solo dev — commit directly to `main`.
- **File renames**: use `git mv`; do not delete and re-create.

---

## 7. Agent principles

- **KISS**: prefer the simplest option; reduce complexity.
- **Follow conventions**: formatting, naming, structure.
- **No speculative implementation**: do not add modules, endpoints, or
  infrastructure for a future phase; add only when the feature is in
  the current todo (`docs/TODO.md`).
- **Boy scout rule**: leave anything you touch cleaner than you found
  it.
- **Root cause**: find it; address causes, not only symptoms.
- **Consistency**: be consistent across the project (terms, tone,
  layout).

---

## 8. Answer format

When a reply presents multiple options or alternatives, list at least
one pro and one con for each option. Keep each pro/con to one short
line. Omit only when options are trivial or the user asks for no
comparison.

---

## 9. Task completion

When finishing code changes, run `ruff format .` and `pytest`; fix any
failures before considering the task complete. If the change touches
DB-dependent code, run `pytest` with `DATABASE_URL` and `NEO4J_*` set
as well.

---

## Rule index (task type → sections)

| Task type | Sections |
| --- | --- |
| Always | §C (language), §I (agent principles), §O (answer format), §W (task completion) |
| Feature / new code | §4 (coding), §5 (commit), §9 (task completion) |
| Refactor | §4 (coding), §5 (commit), §9 (task completion) |
| Docs | §2 (naming), §4 (language) |
| Commit | §5 (commit format), §6 (git) |
| Directory change | §2 (structure and naming) |
| Dependency | §4 (dependencies) |
| DB / migration | §4 (models), §3 (test) |

**Legend**: §C = §4 language; §I = §7; §O = §8; §W = §9; §A = §5;
§D = §2; §E = §4 error handling; §F = §4 function length; §G = §6;
§L = §4 line length; §M = §4 models; §N = §4 type annotations;
§P = §4 imports; §T = §3 test.
