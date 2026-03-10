"""CLI for init_lexis_item: argparse and run loop."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    import argparse

    from app.scripts.init_lexis_item import (
        DEFAULT_LEXIS_INPUT,
        init_from_json,
        init_synsets_from_json,
    )

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
        "--input-file",
        type=Path,
        default=None,
        help="Single JSON file (e.g. temp/oewn/oewn_2025_senses.json)",
    )
    parser.add_argument(
        "--synsets-file",
        type=Path,
        default=None,
        help="Synsets JSON (oewn_2025_synsets.json); load HYPERNYM edges",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only discover files and count, do not write",
    )
    args = parser.parse_args()

    if args.input_file is not None:
        single = args.input_file.resolve()
        if not single.is_file():
            print(f"Not a file: {single}", file=sys.stderr)
            return 1
        json_paths = [single]
    else:
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
                data = __import__("json").load(f)
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
    if args.synsets_file is not None and not args.dry_run:
        synsets_path = args.synsets_file.resolve()
        if synsets_path.is_file():
            n_hypernyms = init_synsets_from_json(synsets_path, graph)
            print(f"{synsets_path.name}: {n_hypernyms} HYPERNYM edges")
        else:
            print(f"Not a file: {synsets_path}", file=sys.stderr)
            return 1
    print(f"Done: {total_lists} lexis sets, {total_items} lexis items")
    return 0
