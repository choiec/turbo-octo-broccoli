"""Init LexisSet (SQLite) and LexisItem (FalkorDB) from lexis JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LEXIS_INPUT = _ROOT / "temp" / "lexis"


def _book_slug(path: Path) -> str:
    """e.g. lexis-middle-basic.json -> middle-basic."""
    stem = path.stem
    if stem.startswith("lexis-"):
        return stem[6:]
    return stem


def init_from_json(
    path: Path,
    graph,
    session,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one JSON; upsert LexisSet and LexisItem. Returns (sets, items)."""
    from app.crud.english.inventory import lexis, lexis_item, lexis_set

    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    if not items:
        return 0, 0

    source = _book_slug(path)
    set_ids_seen: set[str] = set()
    item_count = 0

    for raw in items:
        index = raw.get("index")
        headword = (raw.get("headword") or "").strip()
        unit_num = int(raw.get("day", 0))
        definition = (raw.get("oewnDef") or "").strip()
        pos = (raw.get("oewnPos") or "").strip() or None
        if not headword:
            continue

        item_id = f"{source}-{index}"
        set_id = f"{source}-day-{unit_num:02d}"
        set_ids_seen.add(set_id)

        if not dry_run:
            lexis_item.upsert_lexis_item(
                graph,
                item_id=item_id,
                headword=headword,
                pos=pos,
                definition=definition,
            )
            lexis_item.link_profile(graph, item_id=item_id, headword=headword)
            cefr = lexis.get_dominant_cefr(graph, headword)
            if cefr:
                lexis_item.link_cefr(graph, item_id=item_id, cefr=cefr)

            lexis_set.upsert_lexis_set(
                session,
                set_id=set_id,
                source=source,
                unit_num=unit_num,
            )
            lexis_set.link_item(session, set_id=set_id, item_id=item_id)

        item_count += 1

    if not dry_run and item_count:
        session.commit()
    return len(set_ids_seen), item_count


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Init LexisSet (SQLite) and LexisItem (FalkorDB) from JSON"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_LEXIS_INPUT,
        help="Directory containing lexis-*.json files",
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

    json_paths = sorted(input_dir.glob("lexis-*.json"))
    if not json_paths:
        print(f"No lexis-*.json under {input_dir}", file=sys.stderr)
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
    total_lists = 0
    total_items = 0
    for path in json_paths:
        n_lists, n_items = init_from_json(path, graph, session, dry_run=False)
        total_lists += n_lists
        total_items += n_items
        print(f"{path.name}: {n_items} items, {n_lists} lists")
    print(f"Done: {total_lists} lexis sets, {total_items} lexis items")
    return 0
