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
| **app/models/common/** | Domain-agnostic classification: ObjectType, Concept, LinkType (SQLite). |
| **app/schemas/** | Request/response schemas when separate from models. |
| **app/crud/** | DB query functions for SQLite and FalkorDB. |
| **app/crud/english/inventory/testlet.py** | Testlet graph (FalkorDB); Source is in SQLite. |
| **app/models/english/source.py** | Source table (exam source metadata). |
| **app/crud/english/records/source.py** | Source CRUD (SQLite). |
| **app/core/config.py** | Pydantic Settings; reads env vars from `.env`. |
| **app/core/sqlite.py** | SQLAlchemy engine + `get_session()` FastAPI dependency. |
| **app/core/falkordb.py** | FalkorDB client + `get_graph_conn()` + `init_graph_schema()`. |
| **scripts/init_english_profile.py** | Init grammar/lexis from TSV/CSV (run manually). CefrLevel nodes come from Concept table via `cefr.ensure_cefr_levels()` at startup. |
| **scripts/_data/common/** | TOML: object_types.toml, concepts.toml (CEFR a1..c2, english_source testlet/book), link_types.toml. |
| **scripts/init_concepts.py** | Load config TOML into SQLite (ObjectType, Concept, LinkType). Scheme-agnostic. Run: `uv run python scripts/init_concepts.py`. |

---

## Infrastructure

- **SQLite** — relational storage. Client: `app/core/sqlite.py`
  (`get_session()`). Schema via SQLModel. Env: `SQLITE_PATH`
  (default: `./data/learner_portfolio.db`; no external server required).
- **FalkorDB** — graph storage for the knowledge domain (grammar, lexis, Testlet
  nodes; Testlet holds passage + questions and references Source via source_id).
  Source metadata lives in SQLite. Client: `app/core/falkordb.py`
  (`get_graph_conn()`). Env: `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_GRAPH`
  (default: localhost:56379, graph `knowledge_graph`). When using Docker,
  FalkorDB is not exposed to the host. Testlet init: `uv run python scripts/init_testlet.py`.

---

## Consumers

- **Copilot Studio agents** — call this API directly via HTTP. No
  human-facing UI is in scope.
