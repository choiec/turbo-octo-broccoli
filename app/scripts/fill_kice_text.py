"""Extract passage from p{n}_stem into p{n}_text when p{n}_text is empty."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KICE_JSON_DIR = Path(__file__).resolve().parents[2] / "temp" / ".json" / "task"


def _split_stem(stem: str) -> tuple[str, str]:
    """Split stem into (question, passage). Question ends with ?; passage follows."""
    if not stem:
        return stem, ""
    # Find first "?" followed by optional [N점] and newline (end of Korean question)
    m = re.search(r"\?\s*(?:\[\d+점\])?\s*\n", stem)
    if not m:
        return stem, ""
    end = m.end()
    question = stem[:end].strip()
    passage = stem[end:].strip()
    if not passage or len(passage) < 20:
        return stem, ""
    return question, passage


def fill_text_in_json(json_path: Path) -> int:
    """Fill empty p{n}_text from p{n}_stem. Returns count of updated fields."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    count = 0
    for n in range(18, 41):
        text_key = f"p{n}_text"
        stem_key = f"p{n}_stem"
        if text_key not in data or stem_key not in data:
            continue
        if data[text_key].strip():
            continue
        stem = data[stem_key]
        if not stem.strip():
            continue
        question, passage = _split_stem(stem)
        if not passage:
            continue
        data[text_key] = passage
        data[stem_key] = question
        count += 1
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return count


def main() -> None:
    json_dir = KICE_JSON_DIR
    if not json_dir.exists():
        print(f"JSON dir not found: {json_dir}", file=sys.stderr)
        sys.exit(1)
    exam_pattern = re.compile(r"^\d{4}_\d{2}_")
    files = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else [
            p.name
            for p in json_dir.glob("*.json")
            if exam_pattern.match(p.stem)
        ]
    )
    total = 0
    for name in sorted(files):
        path = json_dir / name
        if not path.exists():
            continue
        count = fill_text_in_json(path)
        total += count
        print(f"  {name}: {count} text fields filled")
    print(f"Total: {total} fields filled")


if __name__ == "__main__":
    main()
