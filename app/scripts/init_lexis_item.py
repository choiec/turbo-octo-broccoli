"""Init LexisItem and VocabList (FalkorDB) from lexis JSON files."""

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
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one JSON; upsert VocabList and LexisItem. Returns (lists, items)."""
    from app.crud.english.inventory import lexis, lexis_item, vocab_list

    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    if not items:
        return 0, 0

    book = _book_slug(path)
    list_ids_seen: set[str] = set()
    item_count = 0

    for raw in items:
        index = raw.get("index")
        headword = (raw.get("headword") or "").strip()
        day = int(raw.get("day", 0))
        definition = (raw.get("oewnDef") or "").strip()
        pos = (raw.get("oewnPos") or "").strip() or None
        if not headword:
            continue

        item_id = f"{book}-{index}"
        list_id = f"{book}-day-{day:02d}"
        list_ids_seen.add(list_id)

        if not dry_run:
            lexis_item.upsert_lexis_item(
                graph,
                item_id=item_id,
                headword=headword,
                pos=pos,
                definition=definition,
            )
            cefr = lexis.get_dominant_cefr(graph, headword)
            if cefr:
                lexis_item.link_cefr(graph, item_id=item_id, cefr=cefr)

            vocab_list.upsert_vocab_list(
                graph,
                list_id=list_id,
                name=f"{book} day {day:02d}",
                book=book,
                day_num=day,
            )
            vocab_list.link_item(graph, list_id=list_id, item_id=item_id)

        item_count += 1

    return len(list_ids_seen), item_count


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Init VocabList and LexisItem (FalkorDB) from JSON"
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
        help="Only discover files and count, do not write to graph",
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
    except ImportError:
        print(
            "Run from repo root and ensure app is on PYTHONPATH.",
            file=sys.stderr,
        )
        return 1

    graph = next(get_graph_conn())
    total_lists = 0
    total_items = 0
    for path in json_paths:
        n_lists, n_items = init_from_json(path, graph, dry_run=False)
        total_lists += n_lists
        total_items += n_items
        print(f"{path.name}: {n_items} items, {n_lists} lists")
    print(f"Done: {total_lists} vocab lists, {total_items} lexis items")
    return 0
