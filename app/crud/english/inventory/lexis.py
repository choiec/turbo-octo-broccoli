from __future__ import annotations

import falkordb
from pydantic import BaseModel


class LexisProfile(BaseModel):
    headword: str
    pos: str | None
    total_freq: float
    total_nb_doc: int
    freq: float
    nb_doc: int


_QUERY = (
    "MATCH (l:LexisProfile)-[r:LEXIS_LEVEL]->(c:CefrLevel {code: $cefr}) "
    "RETURN l.headword, l.pos, l.total_freq, l.total_nb_doc, r.freq, r.nb_doc"
)


_DOMINANT_CEFR_QUERY = (
    "MATCH (l:LexisProfile {headword: $headword})"
    "-[r:LEXIS_LEVEL]->(c:CefrLevel) "
    "RETURN c.code ORDER BY r.freq DESC LIMIT 1"
)


def get_dominant_cefr(graph: falkordb.Graph, headword: str) -> str | None:
    """Return the CEFR level with highest freq for this headword, or None."""
    result = graph.query(_DOMINANT_CEFR_QUERY, params={"headword": headword})
    if not result.result_set:
        return None
    return (result.result_set[0][0] or "").lower() or None


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[LexisProfile]:
    result = graph.query(_QUERY, params={"cefr": cefr.lower()})
    return [
        LexisProfile(
            headword=row[0],
            pos=row[1],
            total_freq=float(row[2]) if row[2] is not None else 0.0,
            total_nb_doc=int(row[3]) if row[3] is not None else 0,
            freq=float(row[4]) if row[4] is not None else 0.0,
            nb_doc=int(row[5]) if row[5] is not None else 0,
        )
        for row in result.result_set
    ]


def upsert_lexis_profile(
    graph: falkordb.Graph,
    *,
    headword: str,
    pos: str | None,
    total_freq: float,
    total_nb_doc: int,
    levels: list[tuple[str, float, int]],
) -> None:
    """Create or update LexisProfile and LEXIS_LEVEL edges. Idempotent."""
    node_q = (
        "MERGE (l:LexisProfile {headword: $headword}) "
        "ON CREATE SET l.pos = $pos, l.total_freq = $total_freq, "
        "l.total_nb_doc = $total_nb_doc "
        "ON MATCH SET l.pos = $pos, l.total_freq = $total_freq, "
        "l.total_nb_doc = $total_nb_doc"
    )
    graph.query(
        node_q,
        params={
            "headword": headword,
            "pos": pos or "",
            "total_freq": total_freq,
            "total_nb_doc": total_nb_doc,
        },
    )
    edge_q = (
        "MATCH (l:LexisProfile {headword: $headword}) "
        "MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (l)-[r:LEXIS_LEVEL]->(c) "
        "SET r.freq = $freq, r.nb_doc = $nb_doc"
    )
    for cefr, freq, nb_doc in levels:
        if freq <= 0:
            continue
        graph.query(
            edge_q,
            params={
                "headword": headword,
                "cefr": cefr.lower(),
                "freq": freq,
                "nb_doc": nb_doc,
            },
        )
