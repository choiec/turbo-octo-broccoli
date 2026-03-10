from __future__ import annotations

import threading
from collections.abc import Generator

import falkordb

from app.core.config import settings

_client: falkordb.FalkorDB | None = None
_graph: falkordb.Graph | None = None
_init_lock = threading.Lock()


class GraphDbUnavailableError(RuntimeError):
    """Raised when the graph DB cannot be opened (e.g. connection refused)."""


_INDEX_QUERIES = [
    "CREATE INDEX FOR (n:CefrLevel) ON (n.code)",
    "CREATE INDEX FOR (n:GrammarProfile) ON (n.guideword)",
    "CREATE INDEX FOR (n:LexisProfile) ON (n.headword)",
    "CREATE INDEX FOR (n:Task) ON (n.task_id)",
    "CREATE INDEX FOR (n:TaskItem) ON (n.task_item_id)",
    "CREATE INDEX FOR (n:LexisItem) ON (n.item_id)",
]


def _ensure_db() -> None:
    global _client, _graph
    if _graph is not None:
        return
    with _init_lock:
        if _graph is not None:
            return
        try:
            _client = falkordb.FalkorDB(
                host=settings.falkordb_host, port=settings.falkordb_port
            )
            _graph = _client.select_graph(settings.falkordb_graph)
        except Exception as e:
            err = str(e).lower()
            if "connection" in err or "refused" in err or "timeout" in err:
                raise GraphDbUnavailableError(
                    "Graph database unavailable (e.g. FalkorDB not running)."
                ) from e
            raise
        for q in _INDEX_QUERIES:
            try:
                _graph.query(q)
            except Exception:
                pass


def get_graph_conn() -> Generator[falkordb.Graph, None, None]:
    _ensure_db()
    assert _graph is not None
    yield _graph


def reset_graph() -> None:
    """Delete the graph and clear cached client for next use."""
    global _client, _graph
    _ensure_db()
    with _init_lock:
        if _graph is not None:
            _graph.delete()
        _graph = None
        _client = None


def init_graph_schema() -> None:
    """Init graph DB and indexes (startup or lazily on first use)."""
    _ensure_db()
