"""Lexis tagging: TaskParagraph -> LexisProfile (CONTAINS_LEXIS) and lexis_cefr."""

from __future__ import annotations

import falkordb

_LEVELS = ("a1", "a2", "b1", "b2", "c1")
_LEVEL_TO_NUM = {lev: i + 1 for i, lev in enumerate(_LEVELS)}


def _numeric_to_cefr(value: float) -> str:
    """Map numeric (1..5) to CEFR string (a1..c1)."""
    if value <= 1.5:
        return "a1"
    if value <= 2.5:
        return "a2"
    if value <= 3.5:
        return "b1"
    if value <= 4.5:
        return "b2"
    return "c1"


def _tag_one_task(
    graph: falkordb.Graph,
    task_id: str,
    text: str,
    nlp,
) -> int:
    from app.crud.english.inventory import lexis
    from app.crud.english.inventory import task as task_crud

    content_pos = {"NOUN", "VERB", "ADJ", "ADV"}
    doc = nlp(text.strip())
    lemmas = set(
        tok.lemma_.lower()
        for tok in doc
        if tok.pos_ in content_pos and tok.lemma_.strip()
    )
    for lemma in lemmas:
        task_crud.link_lexis(graph, task_id=task_id, headword=lemma)

    headwords_q = (
        "MATCH (t:TaskParagraph {task_id: $task_id})-[:CONTAINS_LEXIS]->(l:LexisProfile)"
        " RETURN l.headword"
    )
    result = graph.query(headwords_q, params={"task_id": task_id})
    linked = [row[0] for row in result.result_set if row[0]]
    if not linked:
        return len(lemmas)

    levels: list[float] = []
    for hw in linked:
        cefr = lexis.get_dominant_cefr(graph, hw)
        if cefr and cefr in _LEVEL_TO_NUM:
            levels.append(float(_LEVEL_TO_NUM[cefr]))
    if levels:
        avg = sum(levels) / len(levels)
        task_crud.set_task_cefr(
            graph, task_id, lexis_cefr=_numeric_to_cefr(avg)
        )
    return len(lemmas)


def tag_tasks(
    graph: falkordb.Graph,
    task_list: list[tuple[str, str]],
) -> int:
    """Tag given tasks with LexisProfile (CONTAINS_LEXIS) and set lexis_cefr.

    Returns total headword links. Skips (returns 0) if spaCy is not available
    or task_list is empty.
    """
    if not task_list:
        return 0
    try:
        import spacy
    except ImportError:
        return 0
    nlp = spacy.load("en_core_web_sm")
    total = 0
    for task_id, text in task_list:
        if not text.strip():
            continue
        total += _tag_one_task(graph, task_id, text, nlp)
    return total
