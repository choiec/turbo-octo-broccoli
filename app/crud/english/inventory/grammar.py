from __future__ import annotations

import falkordb
from pydantic import BaseModel


class GrammarProfile(BaseModel):
    guideword: str
    super_category: str | None
    sub_category: str | None
    type: str | None
    can_do: str | None = None
    example: str | None = None
    lexical_range: str | None = None
    cefr_level: str | None = None


_QUERY_BY_CEFR = (
    "MATCH (g:GrammarProfile)-[:GRAMMAR_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN g.guideword, g.super_category, g.sub_category, g.type, "
    "g.can_do, g.example, g.lexical_range, c.code"
)

_LIST_BY_GUIDEWORDS_QUERY = (
    "MATCH (g:GrammarProfile) WHERE g.guideword IN $guidewords "
    "OPTIONAL MATCH (g)-[:GRAMMAR_LEVEL]->(c:CefrLevel) "
    "RETURN g.guideword, g.super_category, g.sub_category, g.type, "
    "g.can_do, g.example, g.lexical_range, c.code"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[GrammarProfile]:
    result = graph.query(_QUERY_BY_CEFR, params={"cefr": cefr.lower()})
    return [
        GrammarProfile(
            guideword=row[0],
            super_category=row[1],
            sub_category=row[2],
            type=row[3],
            can_do=row[4] or None,
            example=row[5] or None,
            lexical_range=row[6] or None,
            cefr_level=(row[7].lower() if row[7] else None),
        )
        for row in result.result_set
    ]


def list_by_guidewords(
    graph: falkordb.Graph, guidewords: list[str]
) -> list[GrammarProfile]:
    """Return GrammarProfiles for the given guidewords with CEFR level."""
    if not guidewords:
        return []
    result = graph.query(
        _LIST_BY_GUIDEWORDS_QUERY, params={"guidewords": guidewords}
    )
    return [
        GrammarProfile(
            guideword=row[0],
            super_category=row[1],
            sub_category=row[2],
            type=row[3],
            can_do=row[4] or None,
            example=row[5] or None,
            lexical_range=row[6] or None,
            cefr_level=(row[7].lower() if row[7] else None),
        )
        for row in result.result_set
    ]


def upsert_grammar_profile(
    graph: falkordb.Graph,
    *,
    guideword: str,
    cefr: str,
    super_category: str | None = None,
    sub_category: str | None = None,
    type_: str | None = None,
    can_do: str | None = None,
    example: str | None = None,
    lexical_range: str | None = None,
) -> None:
    """Create or update GrammarProfile node and link to CefrLevel.
    Idempotent."""
    q = (
        "MERGE (g:GrammarProfile {guideword: $guideword}) "
        "ON CREATE SET g.super_category = $super_category, "
        "g.sub_category = $sub_category, g.type = $type, "
        "g.can_do = $can_do, g.example = $example, "
        "g.lexical_range = $lexical_range "
        "ON MATCH SET g.super_category = $super_category, "
        "g.sub_category = $sub_category, g.type = $type, "
        "g.can_do = $can_do, g.example = $example, "
        "g.lexical_range = $lexical_range "
        "WITH g MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (g)-[:GRAMMAR_LEVEL]->(c)"
    )
    graph.query(
        q,
        params={
            "guideword": guideword,
            "cefr": cefr.lower(),
            "super_category": super_category or "",
            "sub_category": sub_category or "",
            "type": type_ or "",
            "can_do": can_do or "",
            "example": example or "",
            "lexical_range": lexical_range or "",
        },
    )
