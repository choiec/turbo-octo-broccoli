from __future__ import annotations

import falkordb
from pydantic import BaseModel


class GrammarProfile(BaseModel):
    guideword: str
    source: str


_QUERY = (
    "MATCH (g:GrammarProfile)-[:GRAMMATICAL_LEVEL]->"
    "(l:CefrLevel {code: $cefr}) "
    "RETURN g.guideword AS guideword, g.source AS source"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[GrammarProfile]:
    result = graph.query(_QUERY, params={"cefr": cefr.upper()})
    return [
        GrammarProfile(guideword=row[0], source=row[1])
        for row in result.result_set
    ]


def upsert_grammar_profile(
    graph: falkordb.Graph,
    *,
    guideword: str,
    source: str,
    cefr: str,
) -> None:
    """Create or update GrammarProfile and link to CefrLevel. Idempotent."""
    q = (
        "MERGE (g:GrammarProfile {guideword: $guideword}) "
        "ON CREATE SET g.source = $source "
        "ON MATCH SET g.source = $source "
        "WITH g MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (g)-[:GRAMMATICAL_LEVEL]->(c)"
    )
    graph.query(
        q,
        params={
            "guideword": guideword,
            "source": source,
            "cefr": cefr.upper(),
        },
    )
