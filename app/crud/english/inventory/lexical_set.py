"""LexicalSet graph: lexical sets (vocabulary set) containing LexisItems."""

from __future__ import annotations

import falkordb
from pydantic import BaseModel


class LexicalSetMeta(BaseModel):
    """Metadata for a single lexical set."""

    set_id: str
    source: str
    unit_num: int


_LIST_ALL_QUERY = "MATCH (s:LexicalSet) RETURN s.set_id, s.source, s.unit_num"


def upsert_lexical_set(
    graph: falkordb.Graph,
    *,
    set_id: str,
    source: str,
    unit_num: int,
) -> None:
    """Create or update LexicalSet node. Idempotent."""
    q = (
        "MERGE (s:LexicalSet {set_id: $set_id}) "
        "ON CREATE SET s.source = $source, s.unit_num = $unit_num "
        "ON MATCH SET s.source = $source, s.unit_num = $unit_num"
    )
    graph.query(
        q,
        params={
            "set_id": set_id,
            "source": source,
            "unit_num": unit_num,
        },
    )


def link_item(
    graph: falkordb.Graph,
    *,
    set_id: str,
    item_id: str,
) -> None:
    """Link LexicalSet to LexisItem via CONTAINS. Idempotent."""
    q = (
        "MATCH (s:LexicalSet {set_id: $set_id}), "
        "(i:LexisItem {item_id: $item_id}) MERGE (s)-[:CONTAINS]->(i)"
    )
    graph.query(q, params={"set_id": set_id, "item_id": item_id})


def list_all(graph: falkordb.Graph) -> list[LexicalSetMeta]:
    """Return all LexicalSet nodes."""
    result = graph.query(_LIST_ALL_QUERY)
    return [
        LexicalSetMeta(
            set_id=row[0],
            source=row[1] or "",
            unit_num=int(row[2]) if row[2] is not None else 0,
        )
        for row in result.result_set
    ]
