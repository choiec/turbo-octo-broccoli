"""TaskItem graph: individual test items linked to Task and CefrLevel."""

from __future__ import annotations

import json

import falkordb
from pydantic import BaseModel


class TaskItem(BaseModel):
    """Response schema for a single task item."""

    task_item_id: str
    number: int
    section: str
    question_type: str
    stem: str
    options: list[str]
    answer: int
    score: int
    cefr: str | None = None


_LIST_QUERY = (
    "MATCH (t:Task {task_id: $task_id})-[:HAS_TASK_ITEM]->(i:TaskItem) "
    "OPTIONAL MATCH (i)-[:CEFR_LEVEL]->(c:CefrLevel) "
    "RETURN i.task_item_id, i.number, i.section, i.question_type, i.stem, "
    "i.options, i.answer, i.score, c.code"
)


def list_by_task(graph: falkordb.Graph, task_id: str) -> list[TaskItem]:
    """Return task items belonging to the given task."""
    result = graph.query(_LIST_QUERY, params={"task_id": task_id})
    items: list[TaskItem] = []
    for row in result.result_set:
        options_raw = row[5]
        if isinstance(options_raw, str):
            options = json.loads(options_raw) if options_raw else []
        else:
            options = list(options_raw) if options_raw else []
        items.append(
            TaskItem(
                task_item_id=row[0],
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


def upsert_task_item(
    graph: falkordb.Graph,
    *,
    task_id: str,
    number: int,
    section: str = "reading",
    question_type: str = "",
    stem: str,
    options: list[str],
    answer: int,
    score: int,
    cefr: str = "",
) -> None:
    """Create or update TaskItem node, link to Task and optionally CefrLevel."""
    task_item_id = f"{task_id}_i{number}"
    options_json = json.dumps(options)

    node_q = (
        "MERGE (i:TaskItem {task_item_id: $task_item_id}) "
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
            "task_item_id": task_item_id,
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
        "MATCH (t:Task {task_id: $task_id}), "
        "(i:TaskItem {task_item_id: $task_item_id}) "
        "MERGE (t)-[:HAS_TASK_ITEM]->(i)"
    )
    graph.query(
        link_q, params={"task_id": task_id, "task_item_id": task_item_id}
    )

    if cefr:
        cefr_q = (
            "MATCH (i:TaskItem {task_item_id: $task_item_id}) "
            "MERGE (c:CefrLevel {code: $cefr}) "
            "MERGE (i)-[:CEFR_LEVEL]->(c)"
        )
        graph.query(
            cefr_q,
            params={"task_item_id": task_item_id, "cefr": cefr.lower()},
        )
