"""GrammaticalSet graph: textbook TOC nodes containing GrammarProfile nodes."""

from __future__ import annotations

import falkordb

from app.crud.english.inventory.grammar import GrammarProfile
from app.schemas.english.inventory.grammatical_set import GrammaticalSetMeta

_LIST_ALL_QUERY = (
    "MATCH (s:GrammaticalSet) RETURN s.set_id, s.source, s.unit_num, s.title"
)

_LIST_BY_SET_QUERY = (
    "MATCH (s:GrammaticalSet {set_id: $set_id})-[:CONTAINS]->(g:GrammarProfile)"
    " RETURN g.guideword, g.super_category, g.sub_category, g.type, "
    "g.can_do, g.example, g.lexical_range"
)


def upsert_grammatical_set(
    graph: falkordb.Graph,
    *,
    set_id: str,
    source: str,
    unit_num: int,
    title: str | None = None,
) -> None:
    """Create or update GrammaticalSet node. Idempotent."""
    q = (
        "MERGE (s:GrammaticalSet {set_id: $set_id}) "
        "ON CREATE SET s.source = $source, s.unit_num = $unit_num, "
        "s.title = $title "
        "ON MATCH SET s.source = $source, s.unit_num = $unit_num, "
        "s.title = $title"
    )
    graph.query(
        q,
        params={
            "set_id": set_id,
            "source": source,
            "unit_num": unit_num,
            "title": title or "",
        },
    )


def link_grammar(
    graph: falkordb.Graph,
    *,
    set_id: str,
    guideword: str,
) -> None:
    """Link GrammaticalSet to GrammarProfile via CONTAINS. Idempotent."""
    q = (
        "MATCH (s:GrammaticalSet {set_id: $set_id}), "
        "(g:GrammarProfile {guideword: $guideword}) "
        "MERGE (s)-[:CONTAINS]->(g)"
    )
    graph.query(q, params={"set_id": set_id, "guideword": guideword})


def list_all(graph: falkordb.Graph) -> list[GrammaticalSetMeta]:
    """Return all GrammaticalSet nodes."""
    result = graph.query(_LIST_ALL_QUERY)
    return [
        GrammaticalSetMeta(
            set_id=row[0],
            source=row[1] or "",
            unit_num=int(row[2]) if row[2] is not None else 0,
            title=row[3] or None,
        )
        for row in result.result_set
    ]


def list_by_grammatical_set(
    graph: falkordb.Graph, set_id: str
) -> list[GrammarProfile]:
    """Return GrammarProfiles in the given GrammaticalSet."""
    result = graph.query(_LIST_BY_SET_QUERY, params={"set_id": set_id})
    return [
        GrammarProfile(
            guideword=row[0],
            super_category=row[1],
            sub_category=row[2],
            type=row[3],
            can_do=row[4] or None,
            example=row[5] or None,
            lexical_range=row[6] or None,
        )
        for row in result.result_set
    ]
