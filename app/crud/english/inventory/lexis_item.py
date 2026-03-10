"""LexisItem graph: items linked to CefrLevel, LexisProfile."""

from __future__ import annotations

import falkordb
from pydantic import BaseModel


class LexisItemSchema(BaseModel):
    """Response schema for a single lexis set item."""

    item_id: str
    headword: str
    pos: str | None
    definition: str
    cefr: str | None = None


class LexisItemWithProfile(LexisItemSchema):
    """LexisItem with optional LexisProfile (total_freq, total_nb_doc)."""

    total_freq: float | None = None
    total_nb_doc: int | None = None


_LIST_BY_ITEM_IDS_QUERY = (
    "MATCH (i:LexisItem) WHERE i.item_id IN $item_ids "
    "OPTIONAL MATCH (i)-[:LEXIS_LEVEL]->(c:CefrLevel) "
    "RETURN i.item_id, i.headword, i.pos, i.definition, c.code"
)

_LIST_BY_ITEM_IDS_WITH_PROFILE_QUERY = (
    "MATCH (i:LexisItem) WHERE i.item_id IN $item_ids "
    "OPTIONAL MATCH (i)-[:LEXIS_LEVEL]->(c:CefrLevel) "
    "OPTIONAL MATCH (i)-[:HAS_PROFILE]->(l:LexisProfile) "
    "RETURN i.item_id, i.headword, i.pos, i.definition, c.code, "
    "l.total_freq, l.total_nb_doc"
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


def link_profile(
    graph: falkordb.Graph,
    *,
    item_id: str,
    headword: str,
) -> None:
    """Link LexisItem to LexisProfile (HAS_PROFILE).
    Idempotent; no-op if profile absent.
    """
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}), "
        "(l:LexisProfile {headword: $headword}) "
        "MERGE (i)-[:HAS_PROFILE]->(l)"
    )
    graph.query(q, params={"item_id": item_id, "headword": headword})


def list_by_item_ids(
    graph: falkordb.Graph, item_ids: list[str]
) -> list[LexisItemSchema]:
    """Return LexisItems for the given item_ids with optional CEFR."""
    if not item_ids:
        return []
    result = graph.query(_LIST_BY_ITEM_IDS_QUERY, params={"item_ids": item_ids})
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


def list_by_item_ids_with_profile(
    graph: falkordb.Graph, item_ids: list[str]
) -> list[LexisItemWithProfile]:
    """Return LexisItems for item_ids with optional CEFR and LexisProfile."""
    if not item_ids:
        return []
    result = graph.query(
        _LIST_BY_ITEM_IDS_WITH_PROFILE_QUERY, params={"item_ids": item_ids}
    )
    return [
        LexisItemWithProfile(
            item_id=row[0],
            headword=row[1] or "",
            pos=row[2] or None,
            definition=row[3] or "",
            cefr=(row[4].lower() if row[4] else None),
            total_freq=(float(row[5]) if row[5] is not None else None),
            total_nb_doc=(int(row[6]) if row[6] is not None else None),
        )
        for row in result.result_set
    ]
