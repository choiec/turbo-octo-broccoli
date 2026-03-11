---
description: |
  Python code conventions: typing, function length, imports, comments.
glob: "**/*.py"
---

**Line length (§L)**: 80 characters maximum.

**Types (§T)**: All functions must have type annotations — parameters and
return type. Use `from __future__ import annotations` at top of file.
No `Any` unless unavoidable; prefer `TypeAlias` over bare strings.

**Function length (§F)**: Function body 2–4 statements. Extract helpers
rather than growing a function. File ≤100 effective lines (blank lines and
comments excluded).

**Imports (§I)**: Absolute imports only — no relative `..` imports.
Group order: stdlib → third-party → local. One blank line between groups.

**Models (§M)**: SQLModel classes in `<domain>/models.py`. Use `Field()`
for all columns with explicit `nullable` and `default`. No raw `dict`
as return type — always use a Pydantic/SQLModel schema.

**Comments (§C)**: Intent only. No prose narrating what the code does.
No `# type: ignore` or `# noqa` unless a comment explains why.

**Error handling (§E)**: Raise `HTTPException` at router layer only.
Domain functions raise plain Python exceptions; routers convert them.

**Naming (§N)**: All file and directory names use `snake_case` — lowercase
letters and underscores only. `core/` files are named after the infrastructure
technology they wrap (`postgres.py`, `neo4j.py`, `config.py`). Router and
model files use a singular domain noun (`grammar.py`, `practice.py`). No
abbreviations, no hyphens.
