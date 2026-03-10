"""Grammar tagging via LLM (option B): TaskParagraph -> GrammarProfile guidewords."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

import falkordb

from app.scripts._grammar_index import DEFAULT_GRAMMAR_CSV, load_grammar_index
from app.scripts._llm_client import build_user_message, call_llm

if TYPE_CHECKING:
    from openai import OpenAI


def _tag_one_task(
    graph: falkordb.Graph,
    task_id: str,
    text: str,
    index: dict[str, list[dict]],
    client: OpenAI,
    *,
    dry_run: bool = False,
) -> int:
    from app.crud.english.inventory import task as task_crud

    valid_guidewords = {
        e["guideword"] for entries in index.values() for e in entries
    }
    matched: set[str] = set()
    for super_cat, entries in index.items():
        if not entries:
            continue
        user = build_user_message(text, super_cat, entries)
        guidewords = call_llm(client, user)
        for gw in guidewords:
            if gw in valid_guidewords:
                matched.add(gw)
    if not dry_run:
        for gw in matched:
            task_crud.link_grammar(graph, task_id=task_id, guideword=gw)
        _grammar_cefr_q = (
            "MATCH (t:TaskParagraph {task_id: $task_id})-[:CONTAINS_GRAMMAR]->"
            "(g:GrammarProfile)-[:GRAMMAR_LEVEL]->(c:CefrLevel) "
            "RETURN c.code"
        )
        res = graph.query(_grammar_cefr_q, params={"task_id": task_id})
        codes = [row[0] for row in res.result_set if row[0]]
        if codes:
            dominant = Counter(codes).most_common(1)[0][0]
            task_crud.set_task_cefr(
                graph, task_id, grammar_cefr=dominant.lower()
            )
    return len(matched)


def tag_tasks(
    graph: falkordb.Graph,
    task_list: list[tuple[str, str]],
    *,
    grammar_csv_path: Path | None = None,
    openai_api_key: str = "",
) -> int:
    """Tag given tasks with grammar guidewords via LLM. Returns total links.

    Skips (returns 0) if openai_api_key is empty or grammar CSV is missing.
    """
    if not openai_api_key or not task_list:
        return 0
    path = grammar_csv_path or DEFAULT_GRAMMAR_CSV
    if not path.is_file():
        return 0
    from openai import OpenAI

    index = load_grammar_index(path)
    if not index:
        return 0
    client = OpenAI(api_key=openai_api_key)
    total = 0
    for task_id, text in task_list:
        if not text.strip():
            continue
        total += _tag_one_task(graph, task_id, text, index, client)
    return total
