# learner-portfolio — Agent Context

Multi-subject tutoring backend. REST API consumed by
Copilot Studio agents.

## Stack

- Runtime: **Python 3.14**
- HTTP: **FastAPI** (OpenAPI 3.1 auto-generated)
- Validation: **Pydantic v2** (via SQLModel)
- DB (relational): **SQLite** via `sqlmodel` + `sqlalchemy`
- DB (graph): **FalkorDB** via `falkordb` Python client
- Server: **uvicorn**
- Tests: `pytest`
- Consumers: **Copilot Studio** agents call this API directly via HTTP (Entra OAuth)

Entry point: `main.py` → `app/routers/`

## Directory layout

```
main.py              # FastAPI() instance, router registration
app/
  routers/
    admin/           # upload, admin-only endpoints
    english/
      records/       # transaction data (practice, assessment, acquisition…)
      inventory/     # graph queries (grammar, lexis — FalkorDB)
  models/
    common/          # ObjectType, Concept, LinkType (SQLite)
    english/         # SQLModel table classes (English domain)
  schemas/           # request/response schemas (when separate from models)
  crud/
    english/
      records/       # SQLite query functions
      inventory/     # FalkorDB query functions (cefr, grammar, lexis, testlet, item)
  core/
    config.py        # pydantic Settings (env vars)
    sqlite.py        # engine + get_session() dependency (SQLite)
    falkordb.py      # client + get_graph_conn() dependency (FalkorDB)
  scripts/           # app-invokable scripts (init_english_profile, init_testlet, etc.)
docs/                # AI-facing governance docs
scripts/             # standalone CLI and data pipelines (init_concepts, classify_cefr, etc.)
tests/
```

## Rules & skills

Rules live in `.cursor/rules/`. Always-applied:
`core-agent.mdc`, `core-tools.mdc`, `core-git.mdc`.

## AI docs

| File | Role |
| --- | --- |
| `docs/CONTEXT.md` | Project context: stack, directory, commands, where to read what |
| `docs/TODO.md` | Implementation single source of truth (modules, infra, consumers) |
| `docs/RULES.md` | Full rule reference — canonical source for all § |
| `docs/RULES_DIGEST.md` | Always-applied rule digest (§C §I §O §W) for agent context |
