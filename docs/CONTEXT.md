---
title: context
description: One-page project context: stack, goal, boundary, and where to read what.
---

# Project context (single read)

One-page summary for onboarding and daily use.\
**Single source of truth for AI and tooling**: `docs/RULES.md`.\
When writing or editing AI-facing docs in this folder, follow RULES.md §D.

---

## 1. Project and stack

- **Name**: learner-portfolio
- **Runtime**: Python 3.14
- **Stack**: FastAPI (HTTP), Pydantic v2 / SQLModel (validation),
  SQLite (relational storage), FalkorDB (graph storage)
- **Entry**: `main.py` (FastAPI app, router registration, startup event)
- **Type checker**: `ty`
- **Linter / formatter**: `ruff`
- **Consumers**: Copilot Studio agents call this API directly via HTTP

---

## 2. Directory structure

```
main.py                  # FastAPI() instance, router registration
app/
  routers/
    admin/               # upload, admin-only endpoints
    english/
      records/           # transaction data (practice, assessment,
                         #   acquisition, proficiency, writing)
      inventory/         # graph queries (grammar, lexis — FalkorDB)
  models/
    common/              # ObjectType, Concept, LinkType (SQLite)
    english/             # SQLModel table classes (English domain)
  schemas/               # request/response schemas (separate from models)
  crud/
    english/
      records/           # SQLite query functions
      inventory/         # FalkorDB query functions (cefr, grammar, lexis, task, task_item)
  core/
    config.py            # pydantic Settings (reads .env)
    sqlite.py            # engine + get_session() dependency
    falkordb.py          # client + get_graph_conn() + init_graph_schema()
  scripts/               # app-invokable scripts (init_english_profile, init_task, etc.)
docs/                    # AI-facing governance docs (this file)
scripts/                 # standalone CLI and data pipelines (init_concepts, etc.)
tests/
```

- **Max depth**: 5 components from root (root not counted).
- **Naming**: `snake_case` only — lowercase letters and underscores; no
  hyphens. Core files named after the technology they wrap
  (`sqlite.py`, `falkordb.py`, `config.py`). Router and model files use
  a singular domain noun (`grammar.py`, `practice.py`).
- **Exceptions**: `.git`, `.cursor`, `.venv`, `__pycache__`,
  `.pytest_cache`, `.ruff_cache`

---

## 3. Run, build, test

- **Install deps**: `uv sync`
- **Dev server**: `uvicorn main:app --reload` (SQLite embedded; set
  `SQLITE_PATH` in `.env`; FalkorDB: `FALKORDB_HOST`, `FALKORDB_PORT`
  default localhost:56379)
- **Docker / docker compose**: Set `API_PORT` (and optionally
  `FALKORDB_BROWSER_PORT` for falkordb-browser) in `.env`; no defaults in
  the repo. FalkorDB is not exposed to the host. Data lives in external
  volumes so stack reloads (e.g. Portainer redeploy) do not wipe data.
  **Before first deploy** create the volumes once: Portainer → Volumes →
  Add volume → `learner_portfolio_app_data` and `learner_portfolio_falkordb_data`;
  or on the host: `docker volume create learner_portfolio_app_data` and
  `docker volume create learner_portfolio_falkordb_data`. For production
  (including Portainer), set `DB_RESET_ON_STARTUP=false`; if `true`, the
  app drops and recreates SQLite and FalkorDB on every startup.
- **CI**: `.github/workflows/ci.yml` — test, build image to GHCR, then
  trigger deploy webhook. Set repo secret `DEPLOY_WEBHOOK_URL` to the
  Portainer stack/service webhook URL for auto redeploy on push to main.
- **Test**: `pytest`
- **Lint / format**: `ruff check .` / `ruff format .`
- **Type check**: `ty check`

---

## 4. Frequently used commands

| Command | Purpose |
| --- | --- |
| `uv sync` | Install / sync dependencies |
| `uvicorn main:app --reload` | Dev server (watch mode) |
| `pytest` | Run all tests |
| `pytest -k <name>` | Run a specific test |
| `ruff check .` | Lint |
| `ruff format .` | Format |
| `ty check` | Type check |

---

## 5. Implementation goal

**One-line goal**: learner-portfolio provides a multi-subject English
tutoring backend — practice, assessment, acquisition, and knowledge
graph queries — as a REST API consumed by Copilot Studio agents.

**Todo source**: `docs/TODO.md`. Add only modules, routes, and
infrastructure listed there; update TODO.md first, then implement.

**Must**: Follow TODO.md for the current phase. Do not add modules,
routes, or infrastructure not in TODO.md. Apply type-check policy
(RULES.md §N).

---

## 6. Where to read what

- **Rules (canonical)**: `docs/RULES.md`
- **Rules digest (always-applied §)**: `docs/RULES_DIGEST.md`
- **Todo (modules, routes, infra)**: `docs/TODO.md`
- **Context (this file)**: `docs/CONTEXT.md`

---

## 7. Rule application flow

- **Always**: `core-agent.mdc` applies §C, §I, §O, §W every session.
  No rule text is duplicated in `.mdc` files.
- **Python code**: `code-py.mdc` applies line length, types, function
  length, imports, models, comments, error handling, naming to all
  `.py` files.
- **By task**: Which § apply per task type is in RULES.md "Rule index".
  Read the index at the start of each code or refactor task.
