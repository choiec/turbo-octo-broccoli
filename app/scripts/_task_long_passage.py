"""Upsert one long-passage task (p41 or p43) and its TaskItems."""

from __future__ import annotations

from typing import Any

import falkordb

from app.scripts._item_builders import long_group_items


def upsert_long_passage(
    data: dict[str, Any],
    source_id: str,
    group_key: str,
    start_num: int,
    sub_count: int,
    graph: falkordb.Graph,
    dry_run: bool,
    tagged_list: list[tuple[str, str]],
) -> int:
    """Upsert TaskParagraph and TaskItems for one long passage. Returns 1 or 0."""
    from app.crud.english.inventory import task
    from app.crud.english.inventory import task_item as task_item_crud

    text_key = f"{group_key}_text"
    if text_key not in data:
        return 0
    text = str(data.get(text_key) or "").strip()
    items = long_group_items(data, group_key, start_num, sub_count)
    question_group = str(start_num)
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
            )
    if not dry_run and text:
        tagged_list.append((task_id, text))
    return 1
