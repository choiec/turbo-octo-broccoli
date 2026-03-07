# learner-portfolio — Agent Context

Multi-subject tutoring backend. REST API consumed by
Copilot Studio agents.

## Stack

- Runtime: **Python 3.14**
- HTTP: **FastAPI** (OpenAPI 3.1 auto-generated)
- Validation: **Pydantic v2** (via SQLModel)
- DB (relational): **PostgreSQL** via `sqlmodel` + `sqlalchemy`
- DB (graph): **Neo4j** via `neo4j` Python driver
- Server: **uvicorn**
- Tests: `pytest`
- Consumers: **Copilot Studio** agents call this API directly via HTTP (Entra OAuth)

Entry point: `main.py` → `app/routers/`

## Directory layout

```
main.py              # FastAPI() instance, router registration
app/
  routers/
    english/         # transaction data (practice, assessment, acquisition…)
    knowledge/       # graph queries (grammar, lexis nodes in Neo4j)
  models/            # SQLModel table classes
  schemas/           # request/response schemas (when separate from models)
  crud/              # DB query functions
  core/
    config.py        # pydantic Settings (env vars)
    postgres.py      # engine + get_session() dependency (PostgreSQL)
    neo4j.py         # driver + get_graph_session() dependency (Neo4j)
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
