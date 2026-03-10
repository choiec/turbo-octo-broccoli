"""Item builders for init_task: parse options and build task item dicts."""

from __future__ import annotations

from typing import Any

_CIRCLE_TO_INT = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}


def answer_to_int(a: str | int) -> int:
    if isinstance(a, int):
        return a
    a = (a or "").strip()
    if a.isdigit():
        return int(a)
    return _CIRCLE_TO_INT.get(a, 0)


def opts(data: dict[str, Any], prefix: str) -> list[str]:
    return [
        str(data.get(f"{prefix}_opt{i}") or "").strip() for i in range(1, 6)
    ]


def regular_item(data: dict[str, Any], n: int) -> dict[str, Any]:
    prefix = f"p{n}"
    stem = str(data.get(f"{prefix}_stem") or "").strip()
    options = opts(data, prefix)
    answer = answer_to_int(str(data.get(f"{prefix}_answer") or ""))
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


def long_group_items(
    data: dict[str, Any], group: str, start_num: int, sub_count: int
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i in range(1, sub_count + 1):
        num = start_num + i - 1
        prefix = f"{group}_q{i}"
        stem = str(data.get(f"{prefix}_stem") or "").strip()
        options = opts(data, prefix)
        answer = answer_to_int(str(data.get(f"{prefix}_answer") or ""))
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
