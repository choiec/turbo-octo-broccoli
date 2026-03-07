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
| **app/routers/english/inventory/** | Graph queries: grammar and lexis nodes (Kùzu). |
| **app/models/english/** | SQLModel table classes for the English domain. |
| **app/schemas/** | Request/response schemas when separate from models. |
| **app/crud/** | DB query functions for SQLite and Kùzu. |
| **app/core/config.py** | Pydantic Settings; reads env vars from `.env`. |
| **app/core/sqlite.py** | SQLAlchemy engine + `get_session()` FastAPI dependency. |
| **app/core/kuzu.py** | Kùzu db + `get_graph_conn()` + `init_graph_schema()`. |

---

## Infrastructure

- **SQLite** — relational storage. Client: `app/core/sqlite.py`
  (`get_session()`). Schema via SQLModel. Env: `SQLITE_PATH`
  (default: `./learner_portfolio.db`; no external server required).
- **Kùzu** — graph storage for the knowledge domain (grammar and lexis
  nodes). Client: `app/core/kuzu.py` (`get_graph_conn()`). Env:
  `KUZU_PATH` (default: `./knowledge_graph`; embedded, no server required).

---

## Consumers

- **Copilot Studio agents** — call this API directly via HTTP. No
  human-facing UI is in scope.
