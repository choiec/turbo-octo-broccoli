"""Init Source + Task + TaskItem from flat JSON (temp/.json/task/*.json)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import falkordb
from sqlmodel import Session

ANSWER_MAP = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}


def _answer_to_int(a: str) -> int:
    a = (a or "").strip()
    return ANSWER_MAP.get(a, 0)


def _opts(data: dict[str, Any], prefix: str) -> list[str]:
    return [
        str(data.get(f"{prefix}_opt{i}") or "").strip() for i in range(1, 6)
    ]


def _regular_item(data: dict[str, Any], n: int) -> dict[str, Any]:
    prefix = f"p{n}"
    stem = str(data.get(f"{prefix}_stem") or "").strip()
    options = _opts(data, prefix)
    answer = _answer_to_int(str(data.get(f"{prefix}_answer") or ""))
    score = int(data.get(f"{prefix}_score") or 2)
    return {
        "number": n,
        "section": "reading",
        "question_type": "",
        "stem": stem,
        "options": options,
        "answer": answer,
        "score": score,
    }


def _long_group_items(
    data: dict[str, Any], group: str, start_num: int, sub_count: int
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i in range(1, sub_count + 1):
        num = start_num + i - 1
        prefix = f"{group}_q{i}"
        stem = str(data.get(f"{prefix}_stem") or "").strip()
        options = _opts(data, prefix)
        answer = _answer_to_int(str(data.get(f"{prefix}_answer") or ""))
        score = int(data.get(f"{prefix}_score") or 2)
        items.append(
            {
                "number": num,
                "section": "reading",
                "question_type": "",
                "stem": stem,
                "options": options,
                "answer": answer,
                "score": score,
            }
        )
    return items


def init_from_json(
    json_path: Path,
    session: Session,
    graph: falkordb.Graph,
    *,
    dry_run: bool = False,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Load flat JSON; upsert Source, Tasks, TaskItems.

    Returns (n_sources, n_tasks, [(task_id, text), ...]) for upserted
    tasks with non-empty text (for grammar tagging).
    """
    from app.crud.english.inventory import task
    from app.crud.english.inventory import task_item as task_item_crud
    from app.crud.english.records import source as source_crud

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    source_id = str(data.get("source_id") or "").strip()
    if not source_id:
        return 0, 0, []

    tagged_list: list[tuple[str, str]] = []

    year = int(data.get("year", 0))
    month = int(data.get("month", 0))
    exam_type = str(data.get("exam_type") or "csat").strip().lower()
    form = (data.get("form") or "").strip() or None
    academic_year = year + 1

    if not dry_run:
        source_crud.upsert_source(
            session,
            source_id=source_id,
            year=year,
            month=month,
            exam_type=exam_type,
            academic_year=academic_year,
            form=form,
        )

    task_count = 0

    # Regular single-item tasks: p18 .. p40
    for n in range(18, 41):
        prefix = f"p{n}"
        if f"{prefix}_stem" not in data:
            continue
        text = str(data.get(f"{prefix}_text") or "").strip()
        item_data = _regular_item(data, n)
        question_group = str(n)
        task_id = f"{source_id}_p{question_group}"
        if not dry_run:
            task.upsert_task(
                graph,
                task_id=task_id,
                source_id=source_id,
                question_group=question_group,
                text=text,
                footnotes="",
            )
            cefr = str(data.get(f"{prefix}_cefr") or "").strip().lower() or ""
            task_item_crud.upsert_task_item(
                graph,
                task_id=task_id,
                number=item_data["number"],
                section=item_data["section"],
                question_type=item_data["question_type"],
                stem=item_data["stem"],
                options=item_data["options"],
                answer=item_data["answer"],
                score=item_data["score"],
                cefr=cefr,
            )
        if not dry_run and text:
            tagged_list.append((task_id, text))
        task_count += 1

    # Long passage p41: items 41, 42
    if "p41_text" in data:
        text = str(data.get("p41_text") or "").strip()
        cefr = str(data.get("p41_cefr") or "").strip().lower() or ""
        items = _long_group_items(data, "p41", 41, 2)
        question_group = "41"
        task_id = f"{source_id}_p{question_group}"
        if not dry_run:
            task.upsert_task(
                graph,
                task_id=task_id,
                source_id=source_id,
                question_group=question_group,
                text=text,
                footnotes="",
            )
            for it in items:
                task_item_crud.upsert_task_item(
                    graph,
                    task_id=task_id,
                    number=it["number"],
                    section=it["section"],
                    question_type=it["question_type"],
                    stem=it["stem"],
                    options=it["options"],
                    answer=it["answer"],
                    score=it["score"],
                    cefr=cefr,
                )
        if not dry_run and text:
            tagged_list.append((task_id, text))
        task_count += 1

    # Long passage p43: items 43, 44, 45
    if "p43_text" in data:
        text = str(data.get("p43_text") or "").strip()
        cefr = str(data.get("p43_cefr") or "").strip().lower() or ""
        items = _long_group_items(data, "p43", 43, 3)
        question_group = "43"
        task_id = f"{source_id}_p{question_group}"
        if not dry_run:
            task.upsert_task(
                graph,
                task_id=task_id,
                source_id=source_id,
                question_group=question_group,
                text=text,
                footnotes="",
            )
            for it in items:
                task_item_crud.upsert_task_item(
                    graph,
                    task_id=task_id,
                    number=it["number"],
                    section=it["section"],
                    question_type=it["question_type"],
                    stem=it["stem"],
                    options=it["options"],
                    answer=it["answer"],
                    score=it["score"],
                    cefr=cefr,
                )
        if not dry_run and text:
            tagged_list.append((task_id, text))
        task_count += 1

    return 1, task_count, tagged_list
