"""LexisItem graph: definition-level items linked to VocabList and CefrLevel."""

from __future__ import annotations

import falkordb
from pydantic import BaseModel


class LexisItemSchema(BaseModel):
    """Response schema for a single vocab-list lexis item."""

    item_id: str
    headword: str
    pos: str | None
    definition: str
    cefr: str | None = None


_LIST_BY_VOCAB_QUERY = (
    "MATCH (v:VocabList {list_id: $list_id})-[:CONTAINS]->(i:LexisItem) "
    "OPTIONAL MATCH (i)-[:LEXIS_LEVEL]->(c:CefrLevel) "
    "RETURN i.item_id, i.headword, i.pos, i.definition, c.code"
)


def upsert_lexis_item(
    graph: falkordb.Graph,
    *,
    item_id: str,
    headword: str,
    pos: str | None,
    definition: str,
) -> None:
    """Create or update LexisItem node. Idempotent."""
    q = (
        "MERGE (i:LexisItem {item_id: $item_id}) "
        "ON CREATE SET i.headword = $headword, i.pos = $pos, "
        "i.definition = $definition "
        "ON MATCH SET i.headword = $headword, i.pos = $pos, "
        "i.definition = $definition"
    )
    graph.query(
        q,
        params={
            "item_id": item_id,
            "headword": headword,
            "pos": pos or "",
            "definition": definition or "",
        },
    )


def link_cefr(
    graph: falkordb.Graph,
    *,
    item_id: str,
    cefr: str,
) -> None:
    """Link LexisItem to CefrLevel via LEXIS_LEVEL. Idempotent."""
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}) "
        "MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (i)-[:LEXIS_LEVEL]->(c)"
    )
    graph.query(q, params={"item_id": item_id, "cefr": cefr.lower()})


def list_by_vocab_list(
    graph: falkordb.Graph, list_id: str
) -> list[LexisItemSchema]:
    """Return LexisItems in the given VocabList with optional CEFR."""
    result = graph.query(_LIST_BY_VOCAB_QUERY, params={"list_id": list_id})
    return [
        LexisItemSchema(
            item_id=row[0],
            headword=row[1] or "",
            pos=row[2] or None,
            definition=row[3] or "",
            cefr=(row[4].lower() if row[4] else None),
        )
        for row in result.result_set
    ]
