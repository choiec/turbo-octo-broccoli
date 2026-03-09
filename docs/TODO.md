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
| **app/crud/english/inventory/task.py** | Task graph (FalkorDB); Source is in SQLite. |
| **app/models/english/source.py** | Source table (exam source metadata). |
| **app/crud/english/records/source.py** | Source CRUD (SQLite). |
| **app/core/config.py** | Pydantic Settings; reads env vars from `.env`. |
| **app/core/sqlite.py** | SQLAlchemy engine + `get_session()` FastAPI dependency. |
| **app/core/falkordb.py** | FalkorDB client + `get_graph_conn()` + `init_graph_schema()`. |
| **app/scripts/init_english_profile.py** | Init grammar/lexis from TSV/CSV (run manually). CefrLevel nodes come from Concept table via `cefr.ensure_cefr_levels()` at startup. |
| **scripts/init_concepts.py** | Load config TOML into SQLite (ObjectType, Concept, LinkType). Scheme-agnostic. Run: `uv run python scripts/init_concepts.py`. |

### Phase 2 — Learner & FSRS models (SQLite) — implemented

| Module | Table | Role |
| --- | --- | --- |
| **app/models/english/learner_profile.py** | `learner_profile` | Learner identity, CEFR level, grade, weekly schedule, session count. |
| **app/models/english/question_log.py** | `question_log` | Assignment history: learner × item, assigned_at, due_date (未출제 필터). |
| **app/models/english/response_log.py** | `response_log` | Per-item answer records: correct/incorrect, duration, source (recall \| direct). |
| **app/models/english/lesson_log.py** | `lesson_log` | Session records: type (regular \| exam_prep), start/end timestamps. |
| **app/models/english/review_schedule.py** | `review_schedule` | FSRS state per learner × item: stability, difficulty, due_date, retrievability. |
| **app/models/english/fsrs_config.py** | `fsrs_config` | Per-learner FSRS W-vector (19 floats). Defaults to FSRS-5 published values. |
| **app/models/english/error_prior.py** | `error_prior` | Level × question_type baseline error rates for cold-start blending. |
| **app/models/english/essay_outcome.py** | `essay_outcome` | 4-axis AES rubric: accuracy, vocabulary, coherence, task_completion + feedback. |
| **app/models/english/exam_period.py** | `exam_period`, `learner_exam_override` | Grade-level exam windows and per-learner overrides. |
| **app/models/english/recall_event.py** | `recall_event` | Raw recall signals from Copilot Studio webhook; processed flag for FSRS batch. |

---

## Infrastructure

- **SQLite** — relational storage. Client: `app/core/sqlite.py`
  (`get_session()`). Schema via SQLModel. Env: `SQLITE_PATH`
  (default: `./learner_portfolio.db`; no external server required).
- **FalkorDB** — graph storage for the knowledge domain (grammar, lexis, Task
  nodes; Task holds passage + questions and references Source via source_id).
  Source metadata lives in SQLite. Client: `app/core/falkordb.py`
  (`get_graph_conn()`). Env: `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_GRAPH`
  (default: localhost:56379, graph `knowledge_graph`). When using Docker,
  FalkorDB is not exposed to the host. Task init: `uv run python scripts/init_task.py`.

---

## Consumers

- **Copilot Studio agents** — call this API directly via HTTP. No
  human-facing UI is in scope.
