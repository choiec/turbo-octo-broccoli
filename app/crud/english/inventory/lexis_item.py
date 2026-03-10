"""LexisItem graph: list and re-export write ops."""

from __future__ import annotations

import falkordb

from app.crud.english.inventory.lexis_item_write import (
    link_cefr,
    link_profile,
    upsert_lexis_item,
)
from app.schemas.english.inventory.lexis_item import (
    LexisItemSchema,
    LexisItemWithProfile,
)

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
