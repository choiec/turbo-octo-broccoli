"""Init Source + Task + TaskItem from chunk JSON (source, id, article, questions[])."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import falkordb
from sqlmodel import Session

CHUNK_ANSWER_MAP = {"A": 1, "B": 2, "C": 3, "D": 4}


def _chunk_answer_to_int(a: str) -> int:
    a = (a or "").strip().upper()
    return CHUNK_ANSWER_MAP.get(a, 0)


def _process_one_chunk(
    data: dict[str, Any],
    session: Session,
    graph: falkordb.Graph,
    dry_run: bool,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Process a single chunk dict; upsert Source, Task, TaskItems.

    Returns (n_sources, n_tasks, [(task_id, text), ...]) for grammar tagging.
    """
    from app.crud.english.inventory import task
    from app.crud.english.inventory import task_item as task_item_crud
    from app.crud.english.records import source as source_crud

    source_id = str(data.get("source") or "").strip()
    chunk_id = str(data.get("id") or "").strip()
    if not source_id or not chunk_id:
        return 0, 0, []

    tagged_list: list[tuple[str, str]] = []
    article = str(data.get("article") or "").strip()
    questions = data.get("questions")
    if not isinstance(questions, list):
        questions = []

    if not dry_run:
        source_crud.upsert_source(
            session,
            source_id=source_id,
            year=None,
            month=None,
            exam_type="external",
            academic_year=None,
            form=None,
            issuer="external",
            source_type="chunk",
        )

    task_id = chunk_id
    question_group = chunk_id

    if not dry_run:
        task.upsert_task(
            graph,
            task_id=task_id,
            source_id=source_id,
            question_group=question_group,
            text=article,
            footnotes="",
        )

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            continue
        stem = str(q.get("question") or "").strip()
        raw_opts = q.get("options")
        if isinstance(raw_opts, list):
            options_list: list[str] = [str(o or "").strip() for o in raw_opts[:5]]
        else:
            options_list = []
        while len(options_list) < 5:
            options_list.append("")
        answer = _chunk_answer_to_int(str(q.get("answer") or ""))

        if not dry_run:
            task_item_crud.upsert_task_item(
                graph,
                task_id=task_id,
                number=i + 1,
                section="reading",
                question_type="",
                stem=stem,
                options=options_list,
                answer=answer,
                score=1,
                cefr="",
            )

    if not dry_run and article:
        tagged_list.append((task_id, article))

    return 1, 1, tagged_list


def init_from_json(
    json_path: Path,
    session: Session,
    graph: falkordb.Graph,
    *,
    dry_run: bool = False,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Load chunk JSON; upsert Source, Tasks, TaskItems.

    Expects a list of chunk objects: {source, split?, id, article, questions[]}.
    Returns (n_sources, n_tasks, [(task_id, text), ...]) for grammar tagging.
    """
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raw = [raw] if isinstance(raw, dict) else []

    total_sources = 0
    total_tasks = 0
    tagged_list: list[tuple[str, str]] = []
    seen_sources: set[str] = set()

    for item in raw:
        if not isinstance(item, dict):
            continue
        _n_sources, n_tasks, tagged = _process_one_chunk(
            item, session, graph, dry_run
        )
        total_tasks += n_tasks
        tagged_list.extend(tagged)
        source_id = str(item.get("source") or "").strip()
        if source_id:
            seen_sources.add(source_id)

    total_sources = len(seen_sources)
    return total_sources, total_tasks, tagged_list
