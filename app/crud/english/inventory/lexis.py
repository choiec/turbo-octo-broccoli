from __future__ import annotations

import falkordb
from pydantic import BaseModel


class LexisProfile(BaseModel):
    headword: str
    pos: str | None
    synset_id: str | None
    ngsl_rank: int | None


_QUERY = (
    "MATCH (l:LexisProfile)-[:LEXICAL_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN l.headword AS headword, l.pos AS pos, l.synset_id AS synset_id,"
    " l.ngsl_rank AS ngsl_rank"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[LexisProfile]:
    result = graph.query(_QUERY, params={"cefr": cefr.upper()})
    return [
        LexisProfile(
            headword=row[0],
            pos=row[1],
            synset_id=row[2],
            ngsl_rank=row[3],
        )
        for row in result.result_set
    ]
