"""Process one source dict: upsert Source, TaskParagraphs, TaskItems."""

from __future__ import annotations

from typing import Any

import falkordb
from sqlmodel import Session

from app.scripts._item_builders import regular_item
from app.scripts._task_long_passage import upsert_long_passage


def process_one_source(
    data: dict[str, Any],
    session: Session,
    graph: falkordb.Graph,
    dry_run: bool,
) -> tuple[int, int, list[tuple[str, str]]]:
    """Process a single source dict; upsert Source, TaskParagraphs, TaskItems.

    Returns (n_sources, n_tasks, [(task_id, text), ...]) for this source.
    """
    from app.crud.english.inventory import task
    from app.crud.english.inventory import task_item as task_item_crud
    from app.crud.english.records import source as source_crud

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

    for n in range(18, 41):
        prefix = f"p{n}"
        if f"{prefix}_stem" not in data:
            continue
        text = str(data.get(f"{prefix}_text") or "").strip()
        item_data = regular_item(data, n)
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
            )
        if not dry_run and text:
            tagged_list.append((task_id, text))
        task_count += 1

    task_count += upsert_long_passage(
        data, source_id, "p41", 41, 2, graph, dry_run, tagged_list
    )
    task_count += upsert_long_passage(
        data, source_id, "p43", 43, 3, graph, dry_run, tagged_list
    )

    return 1, task_count, tagged_list
