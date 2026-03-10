"""Init LexisSet (SQLite) and LexisItem (FalkorDB) from lexis JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.scripts._lexis_item_helpers import book_slug

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LEXIS_INPUT = _ROOT / "temp" / "lexis"


def _is_oewn_format(raw: dict) -> bool:
    """True if record has OEWN sense fields (item_id, synset_id)."""
    return "item_id" in raw and "synset_id" in raw


def init_from_json(
    path: Path,
    graph,
    session,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Load one JSON; upsert LexisSet and LexisItem. Returns (sets, items).

    OEWN format uses 2-pass: nodes first, then item-to-item edges.
    """
    from app.crud.english.inventory import lexis, lexis_item, lexis_set

    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    if not items:
        return 0, 0

    oewn_format = isinstance(items[0], dict) and _is_oewn_format(items[0])
    source = book_slug(path)
    set_ids_seen: set[str] = set()
    item_count = 0

    if oewn_format:
        # Pass 1: nodes and IN_SYNSET / profile / cefr
        for raw in items:
            if not isinstance(raw, dict):
                continue
            item_id = (raw.get("item_id") or "").strip()
            headword = (raw.get("headword") or "").strip()
            pos = (raw.get("pos") or "").strip() or None
            definition = (raw.get("definition") or "").strip()
            synset_id = (raw.get("synset_id") or "").strip() or None
            example = (raw.get("example") or "").strip() or None
            importance = raw.get("importance")
            forms = raw.get("forms") or []
            if not item_id or not headword:
                continue
            if not dry_run:
                lexis_item.upsert_lexis_item(
                    graph,
                    item_id=item_id,
                    headword=headword,
                    pos=pos,
                    definition=definition,
                    synset_id=synset_id,
                    example=example,
                    importance=importance,
                    forms=forms,
                )
                if synset_id:
                    lexis_item.link_in_synset(
                        graph, item_id=item_id, synset_id=synset_id
                    )
                lexis_item.link_profile(
                    graph, item_id=item_id, headword=headword
                )
                cefr = lexis.get_dominant_cefr(graph, headword)
                if cefr:
                    lexis_item.link_cefr(graph, item_id=item_id, cefr=cefr)
            item_count += 1

        # Pass 2: item-to-item edges (antonym, derivation, also, similar)
        if not dry_run:
            for raw in items:
                if not isinstance(raw, dict):
                    continue
                from_id = (raw.get("item_id") or "").strip()
                if not from_id:
                    continue
                for to_id in raw.get("antonym_ids") or []:
                    to_id = (to_id or "").strip()
                    if to_id:
                        lexis_item.link_antonym(
                            graph, from_id=from_id, to_id=to_id
                        )
                for to_id in raw.get("derivation_ids") or []:
                    to_id = (to_id or "").strip()
                    if to_id:
                        lexis_item.link_derivation(
                            graph, from_id=from_id, to_id=to_id
                        )
                for to_id in raw.get("also_ids") or []:
                    to_id = (to_id or "").strip()
                    if to_id:
                        lexis_item.link_also(
                            graph, from_id=from_id, to_id=to_id
                        )
                for to_id in raw.get("similar_ids") or []:
                    to_id = (to_id or "").strip()
                    if to_id:
                        lexis_item.link_similar(
                            graph, from_id=from_id, to_id=to_id
                        )
    else:
        # Legacy book format: single pass, no synset/relation edges
        for raw in items:
            if not isinstance(raw, dict):
                continue
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
                lexis_item.link_profile(
                    graph, item_id=item_id, headword=headword
                )
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


def init_synsets_from_json(path: Path, graph) -> int:
    """Load synsets JSON; create LexisSynset nodes and HYPERNYM edges."""
    from app.crud.english.inventory import lexis_item

    with open(path, encoding="utf-8") as f:
        synsets = json.load(f)
    if not synsets or not isinstance(synsets, list):
        return 0
    count = 0
    for rec in synsets:
        if not isinstance(rec, dict):
            continue
        from_synset_id = (rec.get("synset_id") or "").strip()
        hypernym_ids = rec.get("hypernym_ids") or []
        if not from_synset_id:
            continue
        for to_synset_id in hypernym_ids:
            to_synset_id = (to_synset_id or "").strip()
            if to_synset_id:
                lexis_item.link_synset_hypernym(
                    graph,
                    from_synset_id=from_synset_id,
                    to_synset_id=to_synset_id,
                )
                count += 1
    return count


if __name__ == "__main__":
    from app.scripts._lexis_item_cli import main

    sys.exit(main())
