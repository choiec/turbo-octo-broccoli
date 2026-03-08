"""Seed FalkorDB grammar/lexis inventory.

CefrLevel, LexisProfile, optionally GrammarProfile.
"""

from __future__ import annotations

import csv
from pathlib import Path

import falkordb

_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEXIS_PATH = _ROOT / "temp" / "lexis" / "lexis_seed.csv"


def _parse_ngsl_rank(value: str) -> int | None:
    if not value or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def seed_grammar_lexis(
    graph: falkordb.Graph,
    *,
    lexis_path: Path | None = None,
    grammar_path: Path | None = None,
) -> None:
    """Ensure CefrLevel and seed LexisProfile (optionally GrammarProfile).

    Idempotent. Skips lexis/grammar if the given path is missing.
    """
    from app.crud.english.inventory import cefr, grammar, lexis

    cefr.ensure_cefr_levels(graph)

    path = lexis_path or DEFAULT_LEXIS_PATH
    if path.exists():
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cefr_code = (row.get("cefr") or "").strip()
                if not cefr_code:
                    continue
                lexis.upsert_lexis_profile(
                    graph,
                    headword=(row.get("headword") or "").strip(),
                    cefr=cefr_code,
                    pos=(row.get("pos") or "").strip() or None,
                    synset_id=(row.get("synset_id") or "").strip() or None,
                    ngsl_rank=_parse_ngsl_rank(row.get("ngsl_rank") or ""),
                )

    if grammar_path and grammar_path.exists():
        with open(grammar_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                guideword = (row.get("guideword") or "").strip()
                cefr_code = (row.get("cefr") or "").strip()
                if not guideword or not cefr_code:
                    continue
                grammar.upsert_grammar_profile(
                    graph,
                    guideword=guideword,
                    source=(row.get("source") or "").strip() or "unknown",
                    cefr=cefr_code,
                )
