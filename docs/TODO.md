---
title: todo
description: In-todo modules and infrastructure.
---

# Todo

Single source of truth for in-todo modules and infrastructure.\
Add only modules and infrastructure listed here; update this file
first, then implement.\
API contract: auto-generated OpenAPI from FastAPI (GET /docs).

---

## Modules

| Module | Role |
| --- | --- |
| **main.py** | Server entry: FastAPI app, router registration, startup event (table + graph schema creation). |
| **app/routers/english/records/** | Transaction data: practice, writing assessment, acquisition, learner proficiency, needs analysis, task outcome. |
| **app/routers/english/inventory/** | Graph queries: grammar and lexis nodes (FalkorDB). |
| **app/models/english/** | SQLModel table classes for the English domain. |
| **app/schemas/** | Request/response schemas when separate from models. |
| **app/crud/** | DB query functions for SQLite and FalkorDB. |
| **app/crud/english/inventory/testlet.py** | Testlet graph: upsert Source, Testlet, ExamQuestion (FalkorDB). |
| **app/core/config.py** | Pydantic Settings; reads env vars from `.env`. |
| **app/core/sqlite.py** | SQLAlchemy engine + `get_session()` FastAPI dependency. |
| **app/core/falkordb.py** | FalkorDB client + `get_graph_conn()` + `init_graph_schema()`. |

---

## Infrastructure

- **SQLite** — relational storage. Client: `app/core/sqlite.py`
  (`get_session()`). Schema via SQLModel. Env: `SQLITE_PATH`
  (default: `./data/learner_portfolio.db`; no external server required).
- **FalkorDB** — graph storage for the knowledge domain (grammar, lexis, testlet
  source/testlet/question nodes). Client: `app/core/falkordb.py`
  (`get_graph_conn()`). Env: `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_GRAPH`
  (default: localhost:56379, graph `knowledge_graph`). When using Docker,
  FalkorDB is not exposed to the host. Testlet seed: `uv run python scripts/seed_testlet.py`.

---

## Consumers

- **Copilot Studio agents** — call this API directly via HTTP. No
  human-facing UI is in scope.
