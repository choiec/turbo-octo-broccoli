"""Init Source (SQLite) and Testlet (FalkorDB) from questions CSV. Used by CLI and admin upload API."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import falkordb
from sqlmodel import Session

ANSWER_MAP = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}
OPTION_START = re.compile(r"[①②③④⑤]")


def _exam_type_slug(exam_type: str, month: int) -> str:
    if "대수능" in exam_type or month in (11, 12):
        return "csat"
    return "mock"


def _source_id(year: int, month: int, exam_type: str) -> str:
    return f"{year}_{month:0>2}_{_exam_type_slug(exam_type, month)}"


def _parse_text(text: str) -> tuple[str, list[str]]:
    """Split question text into stem (including passage) and five options."""
    if not text or not text.strip():
        return "", ["", "", "", "", ""]
    first = OPTION_START.search(text)
    if not first:
        return text.strip(), ["", "", "", "", ""]
    stem = text[: first.start()].strip()
    rest = text[first.start() :]
    options: list[str] = []
    for m in OPTION_START.finditer(rest):
        start = m.start()
        end = OPTION_START.search(rest[start + 1 :])
        chunk = rest[start : (start + 1 + end.start()) if end else len(rest)]
        content = chunk.lstrip("①②③④⑤").strip()
        options.append(content)
    while len(options) < 5:
        options.append("")
    return stem, options[:5]


def _answer_to_int(a: str) -> int:
    a = (a or "").strip()
    return ANSWER_MAP.get(a, 0)


def init_from_csv(
    csv_path: Path,
    session: Session,
    graph: falkordb.Graph,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one questions.csv; upsert Source to SQLite, Testlets to graph. Returns (sources, testlets)."""
    from app.crud.english.inventory import testlet
    from app.crud.english.records import source as source_crud

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return 0, 0

    row0 = rows[0]
    year = int(row0["year"])
    month = int(row0["month"])
    exam_type = row0.get("exam_type", "")
    source_id = _source_id(year, month, exam_type)
    academic_year = year + 1

    if not dry_run:
        source_crud.upsert_source(
            session,
            source_id=source_id,
            year=year,
            month=month,
            exam_type=_exam_type_slug(exam_type, month),
            academic_year=academic_year,
        )

    count = 0
    for row in rows:
        num = int(row["number"])
        section = "listening" if num <= 17 else "reading"
        question_type = "listening" if num <= 17 else "long_reading"
        stem, opt_list = _parse_text(row.get("text", ""))
        options_json = json.dumps(opt_list, ensure_ascii=False)
        answer = _answer_to_int(row.get("answer", ""))
        if answer < 1:
            answer = 1
        score = 2

        question_group = str(num)
        testlet_id = f"{source_id}_p{question_group}"
        questions = [
            {
                "number": num,
                "section": section,
                "question_type": question_type,
                "stem": stem,
                "options": options_json,
                "answer": answer,
                "score": score,
            }
        ]
        if not dry_run:
            text = stem if section == "reading" else ""
            testlet.upsert_testlet(
                graph,
                testlet_id=testlet_id,
                source_id=source_id,
                question_group=question_group,
                text=text,
                footnotes="",
                questions=questions,
            )
        count += 1

    return 1, count
