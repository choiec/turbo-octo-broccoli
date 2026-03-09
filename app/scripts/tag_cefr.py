"""Tag KICE JSON questions with CEFR levels from lexis + grammar analysis."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

_LEVELS = ("a1", "a2", "b1", "b2", "c1")
_LEVEL_TO_NUM = {lev: i + 1 for i, lev in enumerate(_LEVELS)}
_NUM_TO_LEVEL = {i + 1: lev for i, lev in enumerate(_LEVELS)}


def _parse_float(value: str) -> float:
    if not value or not value.strip():
        return 0.0
    try:
        return float(value.strip())
    except ValueError:
        return 0.0


def load_lexis_profile(path: Path) -> dict[str, dict[str, float]]:
    """Load lexis TSV into {word: {a1: freq, a2: freq, ..., c1: freq}}."""
    out: dict[str, dict[str, float]] = {}
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            word = (row.get("word") or "").strip()
            if not word:
                continue
            freqs = {
                lev: _parse_float(row.get(f"level_freq@{lev}") or "")
                for lev in _LEVELS
            }
            out[word.lower()] = freqs
    return out


def _dominant_level(freqs: dict[str, float]) -> float:
    """Numeric CEFR (1..5) for dominant level; if all zero, treat as c1 (5)."""
    best_lev = "c1"
    best_freq = 0.0
    for lev in _LEVELS:
        if freqs.get(lev, 0) > best_freq:
            best_freq = freqs[lev]
            best_lev = lev
    return float(_LEVEL_TO_NUM.get(best_lev, 5))


def _get_nlp():
    import spacy

    return spacy.load("en_core_web_sm")


def grammar_score(doc) -> float:
    """Grammar CEFR numeric (1..5) from spaCy doc; max of detected features."""
    scores: list[float] = [1.0]
    sents = list(doc.sents)
    if not sents:
        return 1.0
    n_tokens = sum(len(s) for s in sents)
    avg_tokens = n_tokens / len(sents)
    has_advcl = 0
    has_relcl = False
    has_auxpass_nsubjpass = False
    has_cc = False
    has_mark = False
    has_acl_participle = False
    for tok in doc:
        if tok.dep_ == "cc":
            has_cc = True
        if tok.dep_ == "mark":
            has_mark = True
        if tok.dep_ == "relcl":
            has_relcl = True
        if tok.dep_ in ("auxpass", "nsubjpass"):
            has_auxpass_nsubjpass = True
        if tok.dep_ == "advcl":
            has_advcl += 1
        if tok.dep_ == "acl" and tok.head.pos_ in ("VERB", "AUX"):
            if tok.pos_ in ("VERB", "AUX") and tok.tag_ in ("VBG", "VBN"):
                has_acl_participle = True
    if has_cc:
        scores.append(1.5)
    if has_mark:
        scores.append(2.0)
    if has_relcl or has_auxpass_nsubjpass:
        scores.append(3.0)
    if has_advcl >= 2:
        scores.append(3.5)
    if has_acl_participle:
        scores.append(4.0)
    noun_chunks = list(doc.noun_chunks)
    if noun_chunks:
        avg_span = sum(len(c) for c in noun_chunks) / len(noun_chunks)
        if avg_span > 3:
            scores.append(4.0)
    nouns = [t for t in doc if t.pos_ == "NOUN"]
    if len(nouns) >= 5:
        nominalized = sum(
            1
            for t in nouns
            if t.text.lower().endswith(("tion", "ment", "ness"))
            or (len(t.text) > 4 and t.text.lower().endswith("ity"))
        )
        if nominalized / len(nouns) > 0.2:
            scores.append(5.0)
    if avg_tokens <= 8 and not (has_mark or has_relcl or has_advcl):
        scores.append(1.0)
    return max(scores)


def _korean_ratio(line: str) -> float:
    """Fraction of characters that are Korean (Hangul)."""
    if not line.strip():
        return 0.0
    korean = sum(1 for c in line if "\uac00" <= c <= "\ud7a3")
    return korean / len(line)


def extract_passage(data: dict, n: int) -> str:
    """Get English passage for question n from p{n}_text or p{n}_stem."""
    text_key = f"p{n}_text"
    stem_key = f"p{n}_stem"
    raw = (data.get(text_key) or "").strip()
    if raw:
        return raw
    raw = (data.get(stem_key) or "").strip()
    if not raw:
        return ""
    lines = raw.split("\n")
    english_lines = [
        ln for ln in lines if _korean_ratio(ln) < 0.3 and ln.strip()
    ]
    return "\n".join(english_lines)


def lexis_score(
    text: str, lexis_map: dict[str, dict[str, float]], nlp
) -> float:
    """Average CEFR numeric (1..5) over content words (NOUN, VERB, ADJ, ADV)."""
    if not text.strip():
        return 1.0
    doc = nlp(text)
    content_pos = {"NOUN", "VERB", "ADJ", "ADV"}
    levels: list[float] = []
    for tok in doc:
        if tok.pos_ not in content_pos:
            continue
        lemma = tok.lemma_.lower()
        if lemma in lexis_map:
            levels.append(_dominant_level(lexis_map[lemma]))
        else:
            levels.append(5.0)
    if not levels:
        return 1.0
    return sum(levels) / len(levels)


def score_to_cefr(combined: float) -> str:
    """Map combined numeric (1..5) to CEFR string (a1..c1)."""
    if combined <= 1.5:
        return "a1"
    if combined <= 2.5:
        return "a2"
    if combined <= 3.5:
        return "b1"
    if combined <= 4.5:
        return "b2"
    return "c1"


def tag_passage(
    text: str,
    lexis_map: dict[str, dict[str, float]],
    nlp,
) -> str:
    """Return CEFR string for passage: 0.6 * lexis + 0.4 * grammar."""
    if not text.strip():
        return "a1"
    doc = nlp(text)
    lex = lexis_score(text, lexis_map, nlp)
    gram = grammar_score(doc)
    combined = 0.6 * lex + 0.4 * gram
    return score_to_cefr(combined)


_QUESTION_NUM_RE = re.compile(r"^p(\d+)_(?:stem|text|score)$")


def _question_nums_with_passage(data: dict) -> set[int]:
    out: set[int] = set()
    for key in data:
        m = _QUESTION_NUM_RE.match(key)
        if m:
            n = int(m.group(1))
            if 18 <= n <= 45:
                out.add(n)
    return out


def _insert_cefr_keys(
    data: dict,
    tags: dict[int, str],
) -> dict:
    """Dict with p{n}_cefr inserted after p{n}_score or p{n}_text/p{n}_stem."""
    added: set[int] = set()
    has_score = {n for n in tags if f"p{n}_score" in data}
    result: dict = {}

    def maybe_emit_cefr(n: int, after_score: bool) -> None:
        if n not in tags or n in added:
            return
        if after_score:
            result[f"p{n}_cefr"] = tags[n]
            added.add(n)
        elif n not in has_score:
            result[f"p{n}_cefr"] = tags[n]
            added.add(n)

    for key, value in data.items():
        result[key] = value
        m = _QUESTION_NUM_RE.match(key)
        if m:
            n = int(m.group(1))
            if 18 <= n <= 45:
                after_score = key == f"p{n}_score"
                maybe_emit_cefr(n, after_score)
    return result


def process_file(
    json_path: Path,
    lexis_map: dict[str, dict[str, float]],
    nlp,
    *,
    dry_run: bool = False,
) -> int:
    """Tag one JSON file; insert p{n}_cefr. Returns number of tags added."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    nums = _question_nums_with_passage(data)
    tags: dict[int, str] = {}
    for n in sorted(nums):
        passage = extract_passage(data, n)
        tags[n] = tag_passage(passage, lexis_map, nlp)
    if dry_run:
        return len(tags)
    new_data = _insert_cefr_keys(data, tags)
    json_path.write_text(
        json.dumps(new_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(tags)


def main() -> None:
    import sys

    _ROOT = Path(__file__).resolve().parent.parent.parent
    _LEXIS_PATH = _ROOT / "temp" / "data" / "english" / "lexis_profile.tsv"
    _KICE_JSON_DIR = _ROOT / "temp" / ".json" / "task"

    if not _LEXIS_PATH.exists():
        print(f"Lexis profile not found: {_LEXIS_PATH}", file=sys.stderr)
        sys.exit(1)
    if not _KICE_JSON_DIR.is_dir():
        print(f"KICE JSON dir not found: {_KICE_JSON_DIR}", file=sys.stderr)
        sys.exit(1)

    lexis_map = load_lexis_profile(_LEXIS_PATH)
    nlp = _get_nlp()
    dry_run = "--dry-run" in sys.argv
    total = 0
    exam_pattern = re.compile(r"^\d{4}_\d{2}_")
    for path in sorted(
        p for p in _KICE_JSON_DIR.glob("*.json") if exam_pattern.match(p.stem)
    ):
        n = process_file(path, lexis_map, nlp, dry_run=dry_run)
        total += n
        print(f"{'[dry-run] ' if dry_run else ''}{path.name}: {n} tags")
    print(f"Done. {total} CEFR tag(s) {'would be ' if dry_run else ''}written.")


if __name__ == "__main__":
    main()
