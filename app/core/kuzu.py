from __future__ import annotations

from collections.abc import Generator

import kuzu

from app.core.config import settings

db = kuzu.Database(settings.kuzu_path)

_NODE_DDLS = [
    (
        "CREATE NODE TABLE IF NOT EXISTS GrammarItem"
        "(guideword STRING, source STRING, PRIMARY KEY (guideword))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS LexisItem"
        "(lemma STRING, pos STRING, synset_id STRING, ngsl_rank INT64,"
        " PRIMARY KEY (lemma))"
    ),
    (
        "CREATE NODE TABLE IF NOT EXISTS CefrLevel"
        "(code STRING, PRIMARY KEY (code))"
    ),
]

_REL_DDLS = [
    "CREATE REL TABLE IF NOT EXISTS AT_LEVEL(FROM GrammarItem TO CefrLevel)",
    (
        "CREATE REL TABLE IF NOT EXISTS LEXIS_AT_LEVEL"
        "(FROM LexisItem TO CefrLevel)"
    ),
]


def get_graph_conn() -> Generator[kuzu.Connection, None, None]:
    conn = kuzu.Connection(db)
    yield conn


def init_graph_schema() -> None:
    conn = kuzu.Connection(db)
    for ddl in _NODE_DDLS + _REL_DDLS:
        conn.execute(ddl)
