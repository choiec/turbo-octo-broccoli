"""TaskParagraph graph: link TaskParagraph to GrammarProfile/LexisProfile and set CEFR."""

from __future__ import annotations

import falkordb


def is_grammar_tagged(graph: falkordb.Graph, task_id: str) -> bool:
    """True if this TaskParagraph has at least one CONTAINS_GRAMMAR edge."""
    q = (
        "MATCH (t:TaskParagraph {task_id: $task_id})-[:CONTAINS_GRAMMAR]->() "
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
    """Create TaskParagraph -[:CONTAINS_GRAMMAR]-> GrammarProfile. No-op if missing."""
    q = (
        "MATCH (t:TaskParagraph {task_id: $task_id}) "
        "MATCH (g:GrammarProfile {guideword: $guideword}) "
        "MERGE (t)-[:CONTAINS_GRAMMAR]->(g)"
    )
    graph.query(q, params={"task_id": task_id, "guideword": guideword})


def is_lexis_tagged(graph: falkordb.Graph, task_id: str) -> bool:
    """True if this TaskParagraph has at least one CONTAINS_LEXIS edge."""
    q = (
        "MATCH (t:TaskParagraph {task_id: $task_id})-[:CONTAINS_LEXIS]->() "
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
    """Create TaskParagraph -[:CONTAINS_LEXIS]-> LexisProfile. No-op if missing."""
    q = (
        "MATCH (t:TaskParagraph {task_id: $task_id}) "
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
    """Set lexis_cefr and/or grammar_cefr on TaskParagraph. None = leave unchanged."""
    if lexis_cefr is None and grammar_cefr is None:
        return
    parts: list[str] = []
    params: dict[str, object] = {"task_id": task_id}
    if lexis_cefr is not None:
        parts.append("t.lexis_cefr = $lexis_cefr")
        params["lexis_cefr"] = lexis_cefr.lower()
    if grammar_cefr is not None:
        parts.append("t.grammar_cefr = $grammar_cefr")
        params["grammar_cefr"] = grammar_cefr.lower()
    q = f"MATCH (t:TaskParagraph {{task_id: $task_id}}) SET {', '.join(parts)}"
    graph.query(q, params=params)
