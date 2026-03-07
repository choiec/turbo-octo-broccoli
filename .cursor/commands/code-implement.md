# Implement

Implement modules listed in `docs/TODO.md` using the
skeleton-first, parallel-subagent pattern.

---

## Phase 1 — Main agent setup

### 1. Read context

Read `docs/TODO.md` and `docs/CONTEXT.md` before doing
anything else.

### 2. Add missing dependencies

Add any test or runtime deps not yet in `pyproject.toml`:

```
uv add --dev pytest httpx
```

### 3. Create skeleton files

Create every file listed in `docs/TODO.md` that does not
exist yet. Each file gets one line only:

```python
from __future__ import annotations
```

Create `__init__.py` files for any new packages as well.
Do not write any logic — leave all content for subagents.

### 4. Implement shared infrastructure

Implement files shared across domains directly (do not
delegate to subagents):

- `app/core/auth.py` — Entra ID OAuth dependency
- Any other `app/core/` additions

Shared files are those imported by more than one domain.

---

## Phase 2 — Subagent dispatch (parallel)

Launch one subagent per domain. Domains map to directories:

| Domain | Directories owned |
| --- | --- |
| english | `app/crud/english/`, `app/routers/english/`, `tests/test_english.py` |
| knowledge | `app/crud/knowledge/`, `app/routers/knowledge/`, `tests/test_knowledge.py` |

### Subagent constraints (include in every subagent prompt)

```
CONSTRAINTS — read before writing any code:
- Modify only the files listed in your assignment.
- DO NOT create new files or folders.
- DO NOT modify shared files: main.py, pyproject.toml,
  app/core/*, app/models/*.
- Follow RULES.md §4 (coding conventions) for every file.
```

### Subagent completion checklist

Each subagent must finish in this order:

1. Implement assigned crud and router files.
2. Write tests in the assigned test file.
3. Run `uv run ruff format .`
4. Run `uv run ruff check .` — fix any errors.
5. Run `uv run ty check` — fix any errors.
6. Run `uv run pytest <assigned test file> -v` — fix
   failures before reporting done.
7. Report final exit codes for all four commands.

---

## Phase 3 — Main agent verification

After all subagents finish, run the full test suite:

```
uv run pytest tests/ -v
```

All tests must pass before the task is considered complete.
