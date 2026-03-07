from __future__ import annotations

import kuzu
from pydantic import BaseModel


class GrammarItem(BaseModel):
    guideword: str
    source: str


_QUERY = (
    "MATCH (g:GrammarItem)-[:AT_LEVEL]->(l:CefrLevel {code: $cefr}) "
    "RETURN g.guideword AS guideword, g.source AS source"
)


def list_by_cefr(conn: kuzu.Connection, cefr: str) -> list[GrammarItem]:
    result = conn.execute(_QUERY, parameters={"cefr": cefr.upper()})
    items: list[GrammarItem] = []
    while result.has_next():
        r = result.get_next()
        items.append(GrammarItem(guideword=r[0], source=r[1]))
    return items
