"""Generate a plausible fifth (distractor) option for reading items via LLM."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI

SYSTEM_PROMPT = """\
You are creating a fifth multiple-choice option for an English reading
comprehension item. Given the passage, the question stem, and the four
existing options (one is correct), output exactly one plausible but
INCORRECT fifth option.
Requirements:
- One short phrase or sentence in English.
- Grammatically correct and natural.
- Plausible so it could be chosen by a learner, but clearly wrong
  given the passage.
- No explanation. Return only a JSON object: {"option": "..."}."""


def generate_fifth_option_llm(
    passage: str,
    stem: str,
    options_1_to_4: list[str],
    correct_index: int,
    *,
    api_key: str,
) -> str | None:
    """Call gpt-4o-mini to generate one plausible wrong fifth option.

    Returns None on failure.
    """
    if not api_key or not options_1_to_4:
        return None
    passage_snippet = (passage or "").strip()[:2500]
    stem_snippet = (stem or "").strip()[:500]
    opts_text = "\n".join(
        f"  {i}. {o.strip()}" for i, o in enumerate(options_1_to_4[:4], 1)
    )
    user_content = f"""PASSAGE:
{passage_snippet}

QUESTION:
{stem_snippet}

OPTIONS (1–4; correct answer is option {correct_index}):
{opts_text}

Provide one plausible but incorrect fifth option as JSON: {{"option": "..."}}
"""

    try:
        from openai import OpenAI

        client: OpenAI = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.4,
            max_tokens=150,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
        option = (data.get("option") or "").strip()
        return option if option else None
    except (json.JSONDecodeError, TypeError, Exception):
        return None
