"""Task graph: Task (passage). Source in SQLite. TaskItems are separate."""

from __future__ import annotations

import falkordb

from app.schemas.english.inventory.task import Task

_LIST_BY_CEFR_QUERY = (
    "MATCH (t:Task) "
    "WHERE t.lexis_cefr = $cefr OR t.grammar_cefr = $cefr "
    "RETURN t.task_id, t.source_id, t.question_group, "
    "t.lexis_cefr, t.grammar_cefr"
)


def list_by_cefr(graph: falkordb.Graph, cefr: str) -> list[Task]:
    """Return tasks whose lexis_cefr or grammar_cefr matches the given level."""
    cefr_lower = cefr.strip().lower()
    result = graph.query(_LIST_BY_CEFR_QUERY, params={"cefr": cefr_lower})
    return [
        Task(
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


def is_lexis_tagged(graph: falkordb.Graph, task_id: str) -> bool:
    """True if this Task has at least one CONTAINS_LEXIS edge."""
    q = (
        "MATCH (t:Task {task_id: $task_id})-[:CONTAINS_LEXIS]->() "
        "RETURN 1 LIMIT 1"
    )
    result = graph.query(q, params={"task_id": task_id})
    return len(result.result_set) > 0


def link_lexis(
    graph: falkordb.Graph,
    *,
    task_id: str,
    headword: str,
) -> None:
    """Create Task -[:CONTAINS_LEXIS]-> LexisProfile. No-op if missing."""
    q = (
        "MATCH (t:Task {task_id: $task_id}) "
        "MATCH (l:LexisProfile {headword: $headword}) "
        "MERGE (t)-[:CONTAINS_LEXIS]->(l)"
    )
    graph.query(q, params={"task_id": task_id, "headword": headword})


def set_task_cefr(
    graph: falkordb.Graph,
    task_id: str,
    *,
    lexis_cefr: str | None = None,
    grammar_cefr: str | None = None,
) -> None:
    """Set lexis_cefr and/or grammar_cefr on Task. None = leave unchanged."""
    if lexis_cefr is None and grammar_cefr is None:
        return
    parts: list[str] = []
    params: dict[str, str] = {"task_id": task_id}
    if lexis_cefr is not None:
        parts.append("t.lexis_cefr = $lexis_cefr")
        params["lexis_cefr"] = lexis_cefr.lower()
    if grammar_cefr is not None:
        parts.append("t.grammar_cefr = $grammar_cefr")
        params["grammar_cefr"] = grammar_cefr.lower()
    q = f"MATCH (t:Task {{task_id: $task_id}}) SET {', '.join(parts)}"
    graph.query(q, params=params)
