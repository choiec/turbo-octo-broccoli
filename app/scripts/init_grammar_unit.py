"""Init GrammarSet (SQLite) and GrammarProfile (FalkorDB) from grammar JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_GRAMMAR_INPUT = _ROOT / "temp" / ".json" / "grammar_set"
_GRAMMAR_MD_ROOT = _ROOT / "temp" / "grammar"

_TITLE_RE = re.compile(
    r"^#{2,4}\s+(?:Unit|Appendix)\s+\d+\s+(.+)", re.MULTILINE
)


def _source_slug(path: Path) -> str:
    """e.g. grammar-basic.json -> basic."""
    stem = path.stem
    if stem.startswith("grammar-"):
        return stem[8:]
    return stem


def _unit_title(source: str, unit_num: int) -> str | None:
    """Extract title from temp/grammar/{source}/unit_{unit_num}.md."""
    md = _GRAMMAR_MD_ROOT / source / f"unit_{unit_num}.md"
    if not md.exists():
        return None
    m = _TITLE_RE.search(md.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def _iter_grammar_profiles(items: list) -> list[tuple[dict, int]]:
    """Yield (profile_dict, unit_num) for each grammar profile.
    Supports both flat format (guideword/level at top) and nested format
    (units with grammar_profiles array)."""
    result: list[tuple[dict, int]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        profiles = raw.get("grammar_profiles")
        if profiles is not None:
            unit_id = (raw.get("unit_id") or "").strip()
            unit_num = 0
            if unit_id.startswith("unit_"):
                try:
                    unit_num = int(unit_id[5:])
                except ValueError:
                    pass
            for p in profiles:
                if isinstance(p, dict):
                    result.append((p, unit_num))
        else:
            unit_num = int(raw.get("unit", 0))
            result.append((raw, unit_num))
    return result


def init_from_json(
    path: Path,
    graph,
    session,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one grammar-*.json; upsert profile and set. Returns (sets, items)."""
    from app.crud.english.inventory import grammar, grammar_set

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        return 0, 0
    items = data if isinstance(data, list) else [data]

    source = _source_slug(path)
    set_ids_seen: set[str] = set()
    item_count = 0

    for raw, unit_num in _iter_grammar_profiles(items):
        guideword = (raw.get("guideword") or "").strip()
        level = (raw.get("level") or "").strip().lower()
        if not guideword or not level:
            continue

        set_id = f"{source}-unit-{unit_num:02d}"
        set_ids_seen.add(set_id)

        if not dry_run:
            grammar.upsert_grammar_profile(
                graph,
                guideword=guideword,
                cefr=level,
                super_category=(raw.get("category") or "").strip() or None,
                sub_category=(raw.get("sub_category") or "").strip() or None,
                can_do=(raw.get("can_do") or "").strip() or None,
            )
            grammar_set.upsert_grammar_set(
                session,
                set_id=set_id,
                source=source,
                unit_num=unit_num,
                title=_unit_title(source, unit_num),
            )
            grammar_set.link_grammar(
                session, set_id=set_id, guideword=guideword
            )

        item_count += 1

    if not dry_run and item_count:
        session.commit()
    return len(set_ids_seen), item_count


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Init GrammarSet and GrammarProfile from JSON"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_GRAMMAR_INPUT,
        help="Directory containing grammar-*.json files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only discover files and count, do not write",
    )
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    if not input_dir.is_dir():
        print(f"Not a directory: {input_dir}", file=sys.stderr)
        return 1

    json_paths = sorted(input_dir.glob("grammar-*.json"))
    if not json_paths:
        print(f"No grammar-*.json under {input_dir}", file=sys.stderr)
        return 1

    if args.dry_run:
        for p in json_paths:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            n = len(data) if isinstance(data, list) else 0
            print(f"  {p.name}: {n} items")
        print(f"Would init {len(json_paths)} files (dry run)")
        return 0

    try:
        from app.core.falkordb import get_graph_conn
        from app.core.sqlite import get_session
    except ImportError:
        print(
            "Run from repo root and ensure app is on PYTHONPATH.",
            file=sys.stderr,
        )
        return 1

    graph = next(get_graph_conn())
    session = next(get_session())
    total_sets = 0
    total_items = 0
    for path in json_paths:
        n_sets, n_items = init_from_json(path, graph, session, dry_run=False)
        total_sets += n_sets
        total_items += n_items
        print(f"{path.name}: {n_items} items, {n_sets} sets")
    print(f"Done: {total_sets} grammar sets, {total_items} grammar links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
