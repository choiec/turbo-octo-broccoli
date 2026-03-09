"""Init FalkorDB English inventory and SQLite profile detail from TSV/CSV."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import falkordb
from sqlmodel import Session

_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _ROOT / "data" / "english"
_TEMP_DIR = _ROOT.parent / "temp" / "english_profile_load"
_LEVELS = ("a1", "a2", "b1", "b2", "c1")
_KNOWN_LEVIS_COLS = frozenset(
    {"word", "tag"}
    | {f"level_freq@{lev}" for lev in _LEVELS}
    | {"total_freq@total"}
    | {f"nb_doc@{lev}" for lev in _LEVELS}
    | {"nb_doc@total"}
)

DEFAULT_LEXIS_PATH = _DATA_DIR / "lexis_profile.tsv"
DEFAULT_GRAMMAR_PATH = _DATA_DIR / "grammar_profile.csv"


def _parse_float(value: str) -> float:
    if not value or not value.strip():
        return 0.0
    try:
        return float(value.strip())
    except ValueError:
        return 0.0


def _parse_int(value: str) -> int:
    if not value or not value.strip():
        return 0
    try:
        return int(float(value.strip()))
    except ValueError:
        return 0


def init_lexis_profile(
    graph: falkordb.Graph,
    session: Session,
    *,
    path: Path | None = None,
) -> None:
    """Load lexis from TSV into FalkorDB and SQLite lexis_profile."""
    from app.crud.english.inventory import cefr, lexis
    from app.models.english.lexis_profile import (
        LexisProfile as LexisProfileTable,
    )

    cefr.ensure_cefr_levels(graph)
    src = path or DEFAULT_LEXIS_PATH
    if not src.exists():
        return
    _TEMP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _TEMP_DIR / "lexis_profile.tsv"
    shutil.copy(src, tmp)
    try:
        with open(tmp, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                headword = (row.get("word") or "").strip()
                if not headword:
                    continue
                pos = (row.get("tag") or "").strip() or None
                total_freq = _parse_float(row.get("total_freq@total") or "")
                total_nb_doc = _parse_int(row.get("nb_doc@total") or "")
                levels: list[tuple[str, float, int]] = []
                for lev in _LEVELS:
                    freq = _parse_float(row.get(f"level_freq@{lev}") or "")
                    nb_doc = _parse_int(row.get(f"nb_doc@{lev}") or "")
                    levels.append((lev, freq, nb_doc))
                lexis.upsert_lexis_profile(
                    graph,
                    headword=headword,
                    pos=pos,
                    total_freq=total_freq,
                    total_nb_doc=total_nb_doc,
                    levels=levels,
                )
                for col_name, val in row.items():
                    if col_name in _KNOWN_LEVIS_COLS:
                        continue
                    if "@" not in col_name:
                        continue
                    freq = _parse_float(val)
                    if freq <= 0:
                        continue
                    parts = col_name.rsplit("@", 1)
                    if len(parts) != 2:
                        continue
                    corpus_name, cefr_level = parts
                    session.merge(
                        LexisProfileTable(
                            headword=headword,
                            corpus_name=corpus_name,
                            cefr_level=cefr_level.lower(),
                            freq=freq,
                        )
                    )
        session.commit()
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def init_grammar_profile(
    graph: falkordb.Graph,
    session: Session,
    *,
    path: Path | None = None,
) -> None:
    """Load grammar from CSV into FalkorDB and SQLite grammar_profile."""
    from app.crud.english.inventory import cefr, grammar
    from app.models.english.grammar_profile import (
        GrammarProfile as GrammarProfileTable,
    )

    cefr.ensure_cefr_levels(graph)
    src = path or DEFAULT_GRAMMAR_PATH
    if not src.exists():
        return
    _TEMP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _TEMP_DIR / "grammar_profile.csv"
    shutil.copy(src, tmp)
    try:
        with open(tmp, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                guideword = (row.get("guideword") or "").strip()
                level = (row.get("Level") or "").strip().upper()
                if not guideword or not level:
                    continue
                super_category = (
                    row.get("SuperCategory") or ""
                ).strip() or None
                sub_category = (row.get("SubCategory") or "").strip() or None
                type_val = (row.get("type") or "").strip() or None
                grammar.upsert_grammar_profile(
                    graph,
                    guideword=guideword,
                    cefr=level,
                    super_category=super_category,
                    sub_category=sub_category,
                    type_=type_val,
                )
                can_do = (row.get("Can-do statement") or "").strip() or None
                example = (row.get("Example") or "").strip() or None
                lexical_range = (row.get("Lexical Range") or "").strip() or None
                session.merge(
                    GrammarProfileTable(
                        guideword=guideword,
                        can_do=can_do,
                        example=example,
                        lexical_range=lexical_range,
                    )
                )
        session.commit()
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
