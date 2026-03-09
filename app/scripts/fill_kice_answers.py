"""Fill p{n}_answer in temp/kice_json/*.json from KICE answer sheet PDFs."""

from __future__ import annotations

import json
import re
from pathlib import Path

import fitz

INBOX_BASE = Path("/mnt/c/inbox/kice")
KICE_JSON_DIR = Path(__file__).resolve().parents[2] / "temp" / "kice_json"

# source_id (year_month_csat_form) -> (folder_name, answer_file_pattern)
FOLDER_PATTERNS: dict[str, tuple[str, str | list[str]]] = {
    "2020_11": ("2020년_11월_한국교육과정평가원_대수능", "영어_정답표.pdf"),
    "2021_12": (
        "2021년_12월_한국교육과정평가원_대수능",
        "3교시_영여영역_정답표.pdf",
    ),
    "2022_11": (
        "2022년_11월_한국교육과정평가원_대수능",
        "3교시_영여영역_정답표.pdf",
    ),
    "2023_11": (
        "2023년_11월_한국교육과정평가원_대수능",
        "3교시_영여영역_정답표.pdf",
    ),
    "2024_11": (
        "2024년_11월_한국교육과정평가원_대수능",
        "3교시_영여영역_정답표.pdf",
    ),
    "2025_11": (
        "2025년_11월_한국교육과정평가원_대수능",
        "3교시_영어영역_정답표.pdf",
    ),
    "2026_11": (
        "2026년_11월_한국교육과정평가원_대수능",
        ["홀수형 정답.pdf", "짝수형 정답.pdf"],
    ),
}


def _parse_single_page(text: str) -> dict[int, str]:
    tokens = re.findall(r"\d+|[①②③④⑤]", text)
    answers: dict[int, str] = {}
    i = 0
    while i < len(tokens):
        if (
            tokens[i].isdigit()
            and i + 1 < len(tokens)
            and tokens[i + 1] in "①②③④⑤"
        ):
            num = int(tokens[i])
            ans = tokens[i + 1]
            answers[num] = ans
            i += 2
        else:
            i += 1
    return answers


def parse_answer_pdf(pdf_path: Path) -> dict[str, dict[int, str]]:
    """Parse KICE answer PDF. Returns {form: {qnum: answer_symbol}}."""
    doc = fitz.open(pdf_path)
    result: dict[str, dict[int, str]] = {}
    for page in doc:
        text = page.get_text()
        if "홀수" in text:
            form = "odd"
        elif "짝수" in text:
            form = "even"
        else:
            continue
        result[form] = _parse_single_page(text)
    doc.close()
    return result


def parse_answer_pdf_single_form(pdf_path: Path, form: str) -> dict[int, str]:
    """Parse a single-form PDF (e.g. 2026 홀수형 정답.pdf)."""
    doc = fitz.open(pdf_path)
    text = doc.load_page(0).get_text()
    doc.close()
    return _parse_single_page(text)


def find_answer_file(source_id: str) -> Path | None:
    """Resolve answer sheet path for source_id (e.g. 2020_11_csat_even)."""
    parts = source_id.split("_")
    if len(parts) != 4:
        return None
    year, month, exam_type, form = parts
    key = f"{year}_{month}"
    if key not in FOLDER_PATTERNS:
        return None
    folder_name, pattern = FOLDER_PATTERNS[key]
    folder = INBOX_BASE / folder_name
    if not folder.exists():
        return None

    if isinstance(pattern, list):
        form_file = {"odd": pattern[0], "even": pattern[1]}.get(form)
        if not form_file:
            return None
        path = folder / form_file
        return path if path.exists() else None

    path = folder / pattern
    return path if path.exists() else None


def get_answers_for_source(source_id: str) -> dict[int, str] | None:
    """Get {qnum: answer} for the given source_id."""
    parts = source_id.split("_")
    if len(parts) != 4:
        return None
    _, _, _, form = parts

    path = find_answer_file(source_id)
    if not path:
        return None

    if "홀수형" in path.name or "짝수형" in path.name:
        return parse_answer_pdf_single_form(path, form)

    parsed = parse_answer_pdf(path)
    return parsed.get(form)


def answer_keys_for_questions() -> list[tuple[int, str]]:
    """Return (qnum, json_key) for all reading questions 18-45."""
    result: list[tuple[int, str]] = []
    for n in range(18, 41):
        result.append((n, f"p{n}_answer"))
    result.append((41, "p41_q1_answer"))
    result.append((42, "p41_q2_answer"))
    result.append((43, "p43_q1_answer"))
    result.append((44, "p43_q2_answer"))
    result.append((45, "p43_q3_answer"))
    return result


def fill_json_answers(json_path: Path, answers: dict[int, str]) -> int:
    """Update JSON file with answers. Returns count of updated fields."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    count = 0
    for qnum, key in answer_keys_for_questions():
        ans = answers.get(qnum)
        if ans and key in data:
            data[key] = ans
            count += 1
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return count


def main() -> None:
    json_dir = KICE_JSON_DIR
    if not json_dir.exists():
        print(f"JSON dir not found: {json_dir}")
        return

    total = 0
    for json_path in sorted(json_dir.glob("*.json")):
        source_id = json_path.stem
        answers = get_answers_for_source(source_id)
        if not answers:
            print(f"  skip {source_id}: no answer sheet")
            continue
        count = fill_json_answers(json_path, answers)
        total += count
        print(f"  {source_id}: filled {count} answers")

    print(f"Total: {total} answers filled")


if __name__ == "__main__":
    main()
