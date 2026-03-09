"""Task graph: Task (passage). Source in SQLite. TaskItems are separate."""

from __future__ import annotations

import falkordb


def upsert_task(
    graph: falkordb.Graph,
    *,
    task_id: str,
    source_id: str,
    question_group: str,
    text: str,
    footnotes: str = "",
) -> None:
    """Create or update Task node (passage only).
    source_id references Source in SQLite; caller must ensure it exists.
    TaskItems are stored as separate TaskItem nodes linked via HAS_TASK_ITEM.
    """
    q = (
        "MERGE (t:Task {task_id: $task_id}) "
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
    """Return (task_id, text) for all Tasks with non-empty text."""
    q = (
        "MATCH (t:Task) WHERE t.text IS NOT NULL AND t.text <> '' "
        "RETURN t.task_id, t.text"
    )
    result = graph.query(q)
    return [(row[0], row[1]) for row in result.result_set]


def is_grammar_tagged(graph: falkordb.Graph, task_id: str) -> bool:
    """True if this Task has at least one CONTAINS_GRAMMAR edge."""
    q = (
        "MATCH (t:Task {task_id: $task_id})-[:CONTAINS_GRAMMAR]->() "
        "RETURN 1 LIMIT 1"
    )
    result = graph.query(q, params={"task_id": task_id})
    return len(result.result_set) > 0


def link_grammar(
    graph: falkordb.Graph,
    *,
    task_id: str,
    guideword: str,
) -> None:
    """Create Task -[:CONTAINS_GRAMMAR]-> GrammarProfile. No-op if missing."""
    q = (
        "MATCH (t:Task {task_id: $task_id}) "
        "MATCH (g:GrammarProfile {guideword: $guideword}) "
        "MERGE (t)-[:CONTAINS_GRAMMAR]->(g)"
    )
    graph.query(q, params={"task_id": task_id, "guideword": guideword})
