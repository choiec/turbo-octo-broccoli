"""Init grammar_item table (SQLite) from grammar_outlines.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTLINES = (
    _ROOT / "temp" / ".json" / "grammar_item" / "grammar_outlines.json"
)


def init_from_json(path: Path, session) -> int:
    """Load grammar_outlines.json; upsert GrammarItem rows.
    Returns total sessions upserted."""
    from app.crud.english.inventory.grammar_item import upsert

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        sessions = data
    elif isinstance(data, dict):
        sessions = data.get("sessions", [])
    else:
        sessions = []

    for s in sessions:
        if not isinstance(s, dict):
            continue
        upsert(
            session,
            curriculum_id=s.get("curriculum_id", ""),
            session_number=int(s.get("session_number", 0)),
            topic=s.get("topic", ""),
            book_units=s.get("book_units") or [],
        )
    return len(sessions)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Init grammar_item from grammar_outlines.json"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_OUTLINES,
        help="Path to grammar_outlines.json",
    )
    args = parser.parse_args()

    path = args.input.resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    try:
        from app.core.sqlite import get_session
    except ImportError:
        print(
            "Run from repo root and ensure app is on PYTHONPATH.",
            file=sys.stderr,
        )
        return 1

    session = next(get_session())
    total = init_from_json(path, session)
    print(f"Done: {total} grammar item sessions upserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
