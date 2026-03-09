"""Init FalkorDB English inventory and SQLite profile detail from TSV/CSV."""

from __future__ import annotations

import csv
import logging
import shutil
from pathlib import Path

import falkordb
from sqlmodel import Session

_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _ROOT / "temp" / "data" / "english"
_TEMP_DIR = _ROOT / "temp" / "english_profile_load"
_LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
_KNOWN_LEVIS_COLS = frozenset(
    {"word", "tag"}
    | {f"level_freq@{lev}" for lev in _LEVELS}
    | {"total_freq@total"}
    | {f"nb_doc@{lev}" for lev in _LEVELS}
    | {"nb_doc@total"}
)

DEFAULT_LEXIS_PATH = _DATA_DIR / "lexis_profile.csv"
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
) -> int:
    """Load lexis CSV into FalkorDB (profile + CEFR edges) and SQLite
    (per-corpus frequency table). Returns rows loaded."""
    from app.crud.english.inventory import lexis
    from app.models.english.lexis_corpus_freq import LexisCorpusFreq

    src = path or DEFAULT_LEXIS_PATH
    if not src.exists():
        return 0
    use_direct = path is not None
    if not use_direct:
        _TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _TEMP_DIR / "lexis_profile.csv"
        shutil.copy(src, tmp)
        src = tmp
    count = 0
    delimiter = "\t" if src.suffix.lower() == ".tsv" else ","
    try:
        with open(src, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                headword = (row.get("word") or "").strip()
                if not headword:
                    continue
                count += 1
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
                        LexisCorpusFreq(
                            headword=headword,
                            corpus_name=corpus_name,
                            cefr_level=cefr_level.lower(),
                            freq=freq,
                        )
                    )
        session.commit()
    finally:
        if not use_direct and src.exists():
            src.unlink(missing_ok=True)
    return count


def init_grammar_profile(
    graph: falkordb.Graph,
    _session: Session | None = None,
    *,
    path: Path | None = None,
) -> int:
    """Load grammar CSV into FalkorDB (all fields as node properties).
    Returns rows loaded. _session is accepted but unused (kept for call-site
    compatibility with upload router)."""
    from app.crud.english.inventory import grammar

    src = path or DEFAULT_GRAMMAR_PATH
    if not src.exists():
        return 0
    use_direct = path is not None
    if not use_direct:
        _TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _TEMP_DIR / "grammar_profile.csv"
        shutil.copy(src, tmp)
        src = tmp
    count = 0
    try:
        with open(src, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                guideword = (row.get("guideword") or "").strip()
                level = (row.get("Level") or "").strip().lower()
                if not guideword or not level:
                    continue
                count += 1
                grammar.upsert_grammar_profile(
                    graph,
                    guideword=guideword,
                    cefr=level,
                    super_category=(row.get("SuperCategory") or "").strip()
                    or None,
                    sub_category=(row.get("SubCategory") or "").strip() or None,
                    type_=(row.get("type") or "").strip() or None,
                    can_do=(row.get("Can-do statement") or "").strip() or None,
                    example=(row.get("Example") or "").strip() or None,
                    lexical_range=(row.get("Lexical Range") or "").strip()
                    or None,
                )
    finally:
        if not use_direct and src.exists():
            src.unlink(missing_ok=True)
    return count


def init_english_profile(
    graph: falkordb.Graph,
    session: Session,
    *,
    lexis_path: Path | None = None,
    grammar_path: Path | None = None,
) -> None:
    """Load lexis and grammar from TSV/CSV.

    Lexis: FalkorDB (profile + CEFR edges) + SQLite (per-corpus freq).
    Grammar: FalkorDB only (all fields as node properties).
    """
    lexis_src = lexis_path or DEFAULT_LEXIS_PATH
    grammar_src = grammar_path or DEFAULT_GRAMMAR_PATH
    if not lexis_src.exists() or not grammar_src.exists():
        logging.warning(
            "English profile data missing (lexis=%s, grammar=%s); skip load",
            lexis_src,
            grammar_src,
        )
    init_lexis_profile(graph, session, path=lexis_path)
    init_grammar_profile(graph, path=grammar_path)
