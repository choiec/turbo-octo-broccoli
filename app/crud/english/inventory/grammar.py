from __future__ import annotations

import falkordb
from pydantic import BaseModel


class GrammarProfile(BaseModel):
    guideword: str
    super_category: str | None
    sub_category: str | None
    type: str | None


_QUERY = (
    "MATCH (g:GrammarProfile)-[:GRAMMAR_LEVEL]->"
    "(c:CefrLevel {code: $cefr}) "
    "RETURN g.guideword, g.super_category, g.sub_category, g.type"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[GrammarProfile]:
    result = graph.query(_QUERY, params={"cefr": cefr.lower()})
    return [
        GrammarProfile(
            guideword=row[0],
            super_category=row[1],
            sub_category=row[2],
            type=row[3],
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
) -> None:
    """Create or update GrammarProfile and link to CefrLevel. Idempotent."""
    q = (
        "MERGE (g:GrammarProfile {guideword: $guideword}) "
        "ON CREATE SET g.super_category = $super_category, "
        "g.sub_category = $sub_category, g.type = $type "
        "ON MATCH SET g.super_category = $super_category, "
        "g.sub_category = $sub_category, g.type = $type "
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
        },
    )
