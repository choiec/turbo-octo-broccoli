"""Grammar tagging via LLM (B안): Testlet -> GrammarProfile guidewords."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import falkordb

_ROOT = Path(__file__).resolve().parent.parent.parent
_GRAMMAR_DIR = _ROOT / "temp" / "data" / "english"
DEFAULT_GRAMMAR_CSV = _GRAMMAR_DIR / "grammar_profile.csv"

_SYSTEM_PROMPT = """\
You are a grammar analyst for English learner texts.
Given a passage and a list of grammar structures from the Cambridge Grammar
Profile, identify which structures are ACTUALLY PRESENT in the passage.
Return ONLY a JSON object: {"matches": ["guideword1", "guideword2", ...]}.
Use exact guideword strings from the list. Return {"matches": []} if none apply.
No explanations."""


def load_grammar_index(path: Path) -> dict[str, list[dict]]:
    """Read grammar CSV; return SuperCategory -> list of guideword entries."""
    by_super: dict[str, list[dict]] = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            guideword = (row.get("guideword") or "").strip()
            level = (row.get("Level") or "").strip().lower()
            super_cat = (row.get("SuperCategory") or "").strip()
            sub_cat = (row.get("SubCategory") or "").strip()
            if not guideword or not super_cat:
                continue
            entry = {
                "guideword": guideword,
                "sub_category": sub_cat,
                "cefr": level,
            }
            by_super.setdefault(super_cat, []).append(entry)
    return by_super


def _build_user_message(
    text: str, super_category: str, entries: list[dict]
) -> str:
    lines = [
        "PASSAGE:",
        text.strip(),
        "",
        f"GRAMMAR STRUCTURES — SuperCategory: {super_category}",
    ]
    for i, e in enumerate(entries, 1):
        lines.append(
            f"{i}. [{e['cefr']}] {e['sub_category']} > {e['guideword']}"
        )
    lines.append("")
    lines.append("Which of these are present in the passage?")
    return "\n".join(lines)


def _call_llm(client: object, user_content: str) -> list[str]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=500,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
        matches = data.get("matches") or []
        return [str(m).strip() for m in matches if m]
    except (json.JSONDecodeError, TypeError):
        return []


def _tag_one_testlet(
    graph: falkordb.Graph,
    testlet_id: str,
    text: str,
    index: dict[str, list[dict]],
    client: object,
    *,
    dry_run: bool = False,
) -> int:
    from app.crud.english.inventory import testlet as testlet_crud

    valid_guidewords = {
        e["guideword"] for entries in index.values() for e in entries
    }
    matched: set[str] = set()
    for super_cat, entries in index.items():
        if not entries:
            continue
        user = _build_user_message(text, super_cat, entries)
        guidewords = _call_llm(client, user)
        for gw in guidewords:
            if gw in valid_guidewords:
                matched.add(gw)
    if not dry_run:
        for gw in matched:
            testlet_crud.link_grammar(
                graph, testlet_id=testlet_id, guideword=gw
            )
    return len(matched)


def tag_testlets(
    graph: falkordb.Graph,
    testlet_list: list[tuple[str, str]],
    *,
    grammar_csv_path: Path | None = None,
    openai_api_key: str = "",
) -> int:
    """Tag given testlets with grammar guidewords via LLM. Returns total links.

    Skips (returns 0) if openai_api_key is empty or grammar CSV is missing.
    """
    if not openai_api_key or not testlet_list:
        return 0
    path = grammar_csv_path or DEFAULT_GRAMMAR_CSV
    if not path.is_file():
        return 0
    from openai import OpenAI

    index = load_grammar_index(path)
    if not index:
        return 0
    client = OpenAI(api_key=openai_api_key)
    total = 0
    for testlet_id, text in testlet_list:
        if not text.strip():
            continue
        total += _tag_one_testlet(graph, testlet_id, text, index, client)
    return total
