"""TaskParagraph graph: TaskParagraph (passage). Source in SQLite. TaskItems are separate."""

from __future__ import annotations

import falkordb

from app.crud.english.inventory.task_links import (
    is_grammar_tagged,
    is_lexis_tagged,
    link_grammar,
    link_lexis,
    set_task_cefr,
)  # noqa: F401 — re-export for callers that import task
from app.schemas.english.inventory.task import TaskParagraph

__all__ = [
    "fetch_all",
    "is_grammar_tagged",
    "is_lexis_tagged",
    "link_grammar",
    "link_lexis",
    "list_by_cefr",
    "set_task_cefr",
    "upsert_task",
]

_LIST_BY_CEFR_QUERY = (
    "MATCH (t:TaskParagraph) "
    "WHERE t.lexis_cefr = $cefr OR t.grammar_cefr = $cefr "
    "RETURN t.task_id, t.source_id, t.question_group, "
    "t.lexis_cefr, t.grammar_cefr"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[TaskParagraph]:
    """Return task paragraphs whose lexis_cefr or grammar_cefr matches the given level."""
    cefr_lower = cefr.strip().lower()
    result = graph.query(_LIST_BY_CEFR_QUERY, params={"cefr": cefr_lower})
    return [
        TaskParagraph(
            task_id=row[0] or "",
            source_id=row[1] or "",
            question_group=row[2] or "",
            lexis_cefr=row[3].lower() if row[3] else None,
            grammar_cefr=row[4].lower() if row[4] else None,
        )
        for row in result.result_set
    ]


def upsert_task(
    graph: falkordb.Graph,
    *,
    task_id: str,
    source_id: str,
    question_group: str,
    text: str,
    footnotes: str = "",
) -> None:
    """Create or update TaskParagraph node (passage only).
    source_id references Source in SQLite; caller must ensure it exists.
    TaskItems are stored as separate TaskItem nodes linked via HAS_TASK_ITEM.
    """
    q = (
        "MERGE (t:TaskParagraph {task_id: $task_id}) "
        "ON CREATE SET t.source_id = $source_id, "
        "t.question_group = $question_group, t.text = $text, "
        "t.footnotes = $footnotes "
        "ON MATCH SET t.text = $text, t.footnotes = $footnotes"
    )
    graph.query(
        q,
        params={
            "task_id": task_id,
            "source_id": source_id,
            "question_group": question_group,
            "text": text,
            "footnotes": footnotes,
        },
    )


def fetch_all(graph: falkordb.Graph) -> list[tuple[str, str]]:
    """Return (task_id, text) for all TaskParagraphs with non-empty text."""
    q = (
        "MATCH (t:TaskParagraph) WHERE t.text IS NOT NULL AND t.text <> '' "
        "RETURN t.task_id, t.text"
    )
    result = graph.query(q)
    return [(row[0], row[1]) for row in result.result_set]
