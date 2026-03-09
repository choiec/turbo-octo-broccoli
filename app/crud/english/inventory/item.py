"""Item graph: individual test items linked to Testlet and CefrLevel."""

from __future__ import annotations

import json

import falkordb
from pydantic import BaseModel


class Item(BaseModel):
    """Response schema for a single test item."""

    item_id: str
    number: int
    section: str
    question_type: str
    stem: str
    options: list[str]
    answer: int
    score: int
    cefr: str | None = None


_LIST_QUERY = (
    "MATCH (t:Testlet {testlet_id: $testlet_id})-[:HAS_ITEM]->(i:Item) "
    "OPTIONAL MATCH (i)-[:CEFR_LEVEL]->(c:CefrLevel) "
    "RETURN i.item_id, i.number, i.section, i.question_type, i.stem, "
    "i.options, i.answer, i.score, c.code"
)


def list_by_testlet(graph: falkordb.Graph, testlet_id: str) -> list[Item]:
    """Return items belonging to the given testlet."""
    result = graph.query(_LIST_QUERY, params={"testlet_id": testlet_id})
    items: list[Item] = []
    for row in result.result_set:
        options_raw = row[5]
        if isinstance(options_raw, str):
            options = json.loads(options_raw) if options_raw else []
        else:
            options = list(options_raw) if options_raw else []
        items.append(
            Item(
                item_id=row[0],
                number=int(row[1]) if row[1] is not None else 0,
                section=str(row[2] or ""),
                question_type=str(row[3] or ""),
                stem=str(row[4] or ""),
                options=options,
                answer=int(row[6]) if row[6] is not None else 0,
                score=int(row[7]) if row[7] is not None else 0,
                cefr=str(row[8]).lower() if row[8] else None,
            )
        )
    return items


def upsert_item(
    graph: falkordb.Graph,
    *,
    testlet_id: str,
    number: int,
    section: str = "reading",
    question_type: str = "",
    stem: str,
    options: list[str],
    answer: int,
    score: int,
    cefr: str = "",
) -> None:
    """Create or update Item node, link to Testlet and optionally CefrLevel."""
    item_id = f"{testlet_id}_i{number}"
    options_json = json.dumps(options)

    node_q = (
        "MERGE (i:Item {item_id: $item_id}) "
        "ON CREATE SET i.number = $number, i.section = $section, "
        "i.question_type = $question_type, i.stem = $stem, "
        "i.options = $options, i.answer = $answer, i.score = $score "
        "ON MATCH SET i.section = $section, i.question_type = $question_type, "
        "i.stem = $stem, i.options = $options, i.answer = $answer, "
        "i.score = $score"
    )
    graph.query(
        node_q,
        params={
            "item_id": item_id,
            "number": number,
            "section": section or "",
            "question_type": question_type or "",
            "stem": stem or "",
            "options": options_json,
            "answer": answer,
            "score": score,
        },
    )

    link_q = (
        "MATCH (t:Testlet {testlet_id: $testlet_id}), "
        "(i:Item {item_id: $item_id}) MERGE (t)-[:HAS_ITEM]->(i)"
    )
    graph.query(link_q, params={"testlet_id": testlet_id, "item_id": item_id})

    if cefr:
        cefr_q = (
            "MATCH (i:Item {item_id: $item_id}) "
            "MERGE (c:CefrLevel {code: $cefr}) "
            "MERGE (i)-[:CEFR_LEVEL]->(c)"
        )
        graph.query(cefr_q, params={"item_id": item_id, "cefr": cefr.lower()})
