from __future__ import annotations

import kuzu
from pydantic import BaseModel


class LexisItem(BaseModel):
    lemma: str
    pos: str | None
    synset_id: str | None
    ngsl_rank: int | None


_QUERY = (
    "MATCH (l:LexisItem)-[:LEXIS_AT_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN l.lemma AS lemma, l.pos AS pos, l.synset_id AS synset_id,"
    " l.ngsl_rank AS ngsl_rank"
)


def list_by_cefr(conn: kuzu.Connection, cefr: str) -> list[LexisItem]:
    result = conn.execute(_QUERY, parameters={"cefr": cefr.upper()})
    items: list[LexisItem] = []
    while result.has_next():
        r = result.get_next()
        items.append(
            LexisItem(lemma=r[0], pos=r[1], synset_id=r[2], ngsl_rank=r[3])
        )
    return items
