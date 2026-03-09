"""Extract KICE TXT 18-45 into flat JSON per exam form."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
KICE_ROOT = _ROOT / "temp" / ".text" / "kice"
OUT_DIR = _ROOT / "temp" / "kice_json"

OPTION_START = re.compile(r"[①②③④⑤]")
RE_QUESTION_NUM = re.compile(r"^(\d{1,2})\.\s*")
RE_LONG_41_42 = re.compile(r"\[41\s*～\s*42\]")
RE_LONG_43_45 = re.compile(r"\[43\s*～\s*45\]")

# Noise lines to drop
RE_COPYRIGHT = re.compile(
    r"이 문제지에 관한 저작권은 한국교육과정평가원에 있습니다\.?\s*$"
)
RE_FORM_LABEL = re.compile(r"^(홀수형|짝수형)\s*$")
RE_PAGE_DIGITS = re.compile(r"^\d\s*$")  # single digit line (page)
RE_LISTENING_END = re.compile(r"이제 듣기 문제가 끝났습니다.*")
RE_IMAGE = re.compile(r"\[IMAGE\]", re.IGNORECASE)


def parse_dir_metadata(dir_name: str) -> tuple[int, int, str] | None:
    """(year, month, exam_type) from dir name. None if not matched."""
    m = re.match(r"(\d{4})년_(\d{1,2})월_(.+)", dir_name)
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2))
    rest = m.group(3)
    if "대수능" in rest or month in (11, 12):
        exam_type = "csat"
    elif "모의평가" in rest:
        exam_type = "mock"
    else:
        exam_type = "mock"
    return year, month, exam_type


def _is_hwp_derived(path: Path) -> bool:
    """True if file looks like HWP conversion ([IMAGE] in first 200 chars)."""
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(200)
        return bool(RE_IMAGE.search(head))
    except OSError:
        return False


def select_files(dir_path: Path) -> dict[str, tuple[Path | None, Path | None]]:
    """
    Return {"odd": (problem_path, answer_path), "even": (...)}.
    problem_path/answer_path may be None if not found.
    """
    result: dict[str, tuple[Path | None, Path | None]] = {
        "odd": (None, None),
        "even": (None, None),
    }
    problem_odd = None
    problem_even = None
    answer_odd = None
    answer_even = None

    for f in dir_path.iterdir():
        if not f.suffix.lower() == ".txt" or not f.is_file():
            continue
        name = f.name
        # Answer key
        if "정답" in name:
            if re.search(r"홀|홀수|\(홀", name):
                answer_odd = f
            elif re.search(r"짝|짝수|\(짝", name):
                answer_even = f
            continue
        # Problem file (skip HWP-derived)
        if _is_hwp_derived(f):
            print(f"Skip HWP-derived: {f}", file=sys.stderr)
            continue
        if "정답" in name or "해설" in name or "듣기" in name:
            continue
        if re.search(r"홀|홀수", name):
            problem_odd = f
        elif re.search(r"짝|짝수", name):
            problem_even = f

    # If only one answer file, use it for both forms
    answer = answer_odd or answer_even
    result["odd"] = (problem_odd, answer_odd or answer)
    result["even"] = (problem_even, answer_even or answer)
    return result


def parse_answer_key(path: Path | None) -> dict[int, tuple[str, int]]:
    """{qnum: (answer_mark, score)} for 1-45. Empty if path None/unreadable."""
    out: dict[int, tuple[str, int]] = {}
    if path is None or not path.exists():
        return out
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return out
    # Tokens appear in order: num, answer, score, num, answer, score, ...
    tokens: list[tuple[int | str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d{1,2}$", line):
            n = int(line)
            if 1 <= n <= 45:
                tokens.append((n, "num"))
        elif OPTION_START.match(line):
            tokens.append((line[0], "ans"))
        elif line in ("2", "3"):
            tokens.append((int(line), "score"))
    nums = [t[0] for t in tokens if t[1] == "num" and isinstance(t[0], int)]
    answers = [t[0] for t in tokens if t[1] == "ans" and isinstance(t[0], str)]
    scores = [t[0] for t in tokens if t[1] == "score" and isinstance(t[0], int)]
    if len(nums) >= 45 and len(answers) >= 45 and len(scores) >= 45:
        for i in range(45):
            out[nums[i]] = (answers[i], scores[i])
    return out


def strip_noise(lines: list[str]) -> list[str]:
    """Drop copyright, form labels, page digits, listening-end announcement."""
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if RE_COPYRIGHT.match(s):
            continue
        if RE_FORM_LABEL.match(s):
            continue
        if RE_PAGE_DIGITS.match(s):
            continue
        if RE_LISTENING_END.match(s):
            continue
        if RE_IMAGE.search(s):
            continue
        out.append(line)
    return out


def _split_stem_and_options(block: str) -> tuple[str, list[str]]:
    """Split block into stem (before first ①-⑤) and list of 5 option strings."""
    if not block or not block.strip():
        return "", ["", "", "", "", ""]
    first = OPTION_START.search(block)
    if not first:
        return block.strip(), ["", "", "", "", ""]
    stem = block[: first.start()].strip()
    rest = block[first.start() :]
    options: list[str] = []
    for m in OPTION_START.finditer(rest):
        start = m.start()
        next_m = OPTION_START.search(rest[start + 1 :])
        end = (start + 1 + next_m.start()) if next_m else len(rest)
        chunk = rest[start:end]
        content = chunk.lstrip("①②③④⑤").strip()
        options.append(content)
    while len(options) < 5:
        options.append("")
    return stem, options[:5]


def _extract_english_passage(stem: str) -> tuple[str, str]:
    """(english_passage, korean_instruction). Passage = leading English."""
    # Korean instruction usually starts with Korean or "다음 글" etc.
    lines = stem.split("\n")
    eng_lines: list[str] = []
    kr_lines: list[str] = []
    in_eng = True
    for line in lines:
        s = line.strip()
        if not s:
            if in_eng:
                eng_lines.append("")
            else:
                kr_lines.append("")
            continue
        # Heuristic: line starting with ASCII/English and no Korean → English
        has_korean = bool(re.search(r"[\uac00-\ud7a3]", s))
        if has_korean and in_eng and eng_lines:
            in_eng = False
        if in_eng and not has_korean and (s[0].isascii() or s.startswith("*")):
            eng_lines.append(line)
        else:
            in_eng = False
            kr_lines.append(line)
    return "\n".join(eng_lines).strip(), "\n".join(kr_lines).strip()


def parse_problem(path: Path, answers: dict[int, tuple[str, int]]) -> dict:
    """Parse problem file; return flat dict p18_*..p40_*, p41_*, p43_*."""
    raw = path.read_text(encoding="utf-8")
    lines = strip_noise(raw.splitlines())
    full_text = "\n".join(lines)

    # Find long-reading block boundaries
    long_41_m = RE_LONG_41_42.search(full_text)
    long_43_m = RE_LONG_43_45.search(full_text)
    block_41 = ""
    block_43 = ""
    if long_41_m and long_43_m:
        block_41 = full_text[long_41_m.start() : long_43_m.start()]
        block_43 = full_text[long_43_m.start() :]
    elif long_41_m:
        block_41 = full_text[long_41_m.start() :]
    elif long_43_m:
        block_43 = full_text[long_43_m.start() :]

    start_18 = long_41_m.start() if long_41_m else len(full_text)
    chunk_18_40 = full_text[:start_18]

    # Extract 18-40: find "18. ", "19. ", ... "40. "
    single_blocks: dict[int, str] = {}
    for num in range(18, 41):
        pat = re.compile(rf"^{num}\.\s*", re.MULTILINE)
        m = pat.search(chunk_18_40)
        if m:
            start = m.start()
            # Next question or end
            next_num = num + 1
            next_pat = re.compile(rf"^{next_num}\.\s*", re.MULTILINE)
            next_m = next_pat.search(chunk_18_40, start + 1)
            end = next_m.start() if next_m else len(chunk_18_40)
            single_blocks[num] = chunk_18_40[start:end].strip()

    # Q18: if block has no English passage, use text after "이제 듣기" in raw
    listen_end = re.search(r"이제 듣기 문제가 끝났습니다.*?\n", raw)
    q18_passage_extra = ""
    if 18 in single_blocks:
        block18 = single_blocks[18]
        passage_18, _ = _extract_english_passage(block18)
        if not passage_18.strip() and listen_end:
            after = raw[listen_end.end() :]
            before_21 = re.split(r"\n\s*21\.\s*", after, maxsplit=1)[0]
            before_copyright = re.split(r"이 문제지에 관한 저작권", before_21)[
                0
            ]
            q18_passage_extra = before_copyright.strip()
            q18_passage_extra = re.sub(
                r"^따라 답을 하시기 바랍니다\.?\s*\n?", "", q18_passage_extra
            ).strip()

    # Strip announcement and stray Q18 letter from blocks 19-40
    for num in range(19, 41):
        if num not in single_blocks:
            continue
        block = single_blocks[num]
        if "이제 듣기 문제가 끝났습니다" in block:
            block = block.split("이제 듣기 문제가 끝났습니다")[0].strip()
        if "따라 답을 하시기 바랍니다" in block:
            block = block.split("따라 답을 하시기 바랍니다")[0].strip()
        # Stray Q18 letter (after strip_noise removed announcement line)
        if "\n\nDear " in block and "Sincerely," in block:
            block = block.split("\n\nDear ")[0].strip()
        single_blocks[num] = block

    flat: dict = {}

    # Single questions 18-40
    for num in range(18, 41):
        block = single_blocks.get(num, "")
        if not block:
            flat[f"p{num}_text"] = q18_passage_extra if num == 18 else ""
            flat[f"p{num}_stem"] = ""
            for i in range(1, 6):
                flat[f"p{num}_opt{i}"] = ""
            flat[f"p{num}_answer"] = answers.get(num, ("", 2))[0]
            flat[f"p{num}_score"] = answers.get(num, ("", 2))[1]
            continue
        stem, options = _split_stem_and_options(block)
        passage, instruction = _extract_english_passage(stem)
        if num == 18 and q18_passage_extra:
            passage = q18_passage_extra
        flat[f"p{num}_text"] = passage
        instruction = instruction or stem
        instruction = re.sub(r"^\d+\.\s*", "", instruction).strip()
        flat[f"p{num}_stem"] = instruction
        for i, opt in enumerate(options, 1):
            flat[f"p{num}_opt{i}"] = opt
        ans, score = answers.get(num, ("", 2))
        flat[f"p{num}_answer"] = ans
        flat[f"p{num}_score"] = score

    # Long 41-42
    if block_41:
        block41 = block_41
        # Remove marker line
        block41 = re.sub(
            r"^\[41\s*～\s*42\].*?물음에 답하시오\.?\s*\n?",
            "",
            block41,
            count=1,
            flags=re.DOTALL,
        )
        # Split by "41. " and "42. "
        m41 = re.search(r"41\.\s*", block41)
        m42 = re.search(r"42\.\s*", block41)
        if m41 and m42:
            passage_41 = block41[: m41.start()].strip()
            q41_text = block41[m41.start() : m42.start()].strip()
            q42_text = block41[m42.start() :].strip()
            flat["p41_text"] = passage_41
            s1, o1 = _split_stem_and_options(q41_text.replace("41.", "", 1))
            s2, o2 = _split_stem_and_options(q42_text.replace("42.", "", 1))
            flat["p41_q1_stem"] = s1.strip()
            for i, o in enumerate(o1, 1):
                flat[f"p41_q1_opt{i}"] = o
            flat["p41_q1_answer"] = answers.get(41, ("", 2))[0]
            flat["p41_q1_score"] = answers.get(41, ("", 2))[1]
            flat["p41_q2_stem"] = s2.strip()
            for i, o in enumerate(o2, 1):
                flat[f"p41_q2_opt{i}"] = o
            flat["p41_q2_answer"] = answers.get(42, ("", 2))[0]
            flat["p41_q2_score"] = answers.get(42, ("", 2))[1]
        else:
            flat["p41_text"] = block41
            flat["p41_q1_stem"] = flat["p41_q2_stem"] = ""
            for i in range(1, 6):
                flat[f"p41_q1_opt{i}"] = flat[f"p41_q2_opt{i}"] = ""
            flat["p41_q1_answer"] = flat["p41_q2_answer"] = ""
            flat["p41_q1_score"] = flat["p41_q2_score"] = 2
    else:
        flat["p41_text"] = ""
        flat["p41_q1_stem"] = flat["p41_q2_stem"] = ""
        for i in range(1, 6):
            flat[f"p41_q1_opt{i}"] = flat[f"p41_q2_opt{i}"] = ""
        flat["p41_q1_answer"] = flat["p41_q2_answer"] = ""
        flat["p41_q1_score"] = flat["p41_q2_score"] = 2

    # Long 43-45
    if block_43:
        block43 = block_43
        block43 = re.sub(
            r"^\[43\s*～\s*45\].*?물음에 답하시오\.?\s*\n?",
            "",
            block43,
            count=1,
            flags=re.DOTALL,
        )
        m43 = re.search(r"43\.\s*", block43)
        m44 = re.search(r"44\.\s*", block43)
        m45 = re.search(r"45\.\s*", block43)
        if m43 and m44 and m45:
            passage_43 = block43[: m43.start()].strip()
            q43_t = block43[m43.start() : m44.start()].strip()
            q44_t = block43[m44.start() : m45.start()].strip()
            q45_t = block43[m45.start() :].strip()
            flat["p43_text"] = passage_43
            for qidx, (qnum, qtext) in enumerate(
                [(43, q43_t), (44, q44_t), (45, q45_t)], 1
            ):
                stem, opts = _split_stem_and_options(
                    qtext.replace(f"{qnum}.", "", 1)
                )
                flat[f"p43_q{qidx}_stem"] = stem.strip()
                for i, o in enumerate(opts, 1):
                    flat[f"p43_q{qidx}_opt{i}"] = o
                flat[f"p43_q{qidx}_answer"] = answers.get(qnum, ("", 2))[0]
                flat[f"p43_q{qidx}_score"] = answers.get(qnum, ("", 2))[1]
        else:
            flat["p43_text"] = block43
            for qidx in range(1, 4):
                flat[f"p43_q{qidx}_stem"] = ""
                for i in range(1, 6):
                    flat[f"p43_q{qidx}_opt{i}"] = ""
                flat[f"p43_q{qidx}_answer"] = ""
                flat[f"p43_q{qidx}_score"] = 2
    else:
        flat["p43_text"] = ""
        for qidx in range(1, 4):
            flat[f"p43_q{qidx}_stem"] = ""
            for i in range(1, 6):
                flat[f"p43_q{qidx}_opt{i}"] = ""
            flat[f"p43_q{qidx}_answer"] = ""
            flat[f"p43_q{qidx}_score"] = 2

    return flat


def build_flat(
    year: int, month: int, exam_type: str, form: str, parsed: dict
) -> dict:
    """Build final flat JSON dict with source_id and metadata."""
    source_id = f"{year}_{month:02d}_{exam_type}_{form}"
    out = {
        "source_id": source_id,
        "year": year,
        "month": month,
        "exam_type": exam_type,
        "form": form,
        **parsed,
    }
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not KICE_ROOT.exists():
        print(f"KICE root not found: {KICE_ROOT}", file=sys.stderr)
        return
    count = 0
    for dir_path in sorted(KICE_ROOT.iterdir()):
        if not dir_path.is_dir():
            continue
        meta = parse_dir_metadata(dir_path.name)
        if meta is None:
            continue
        year, month, exam_type = meta
        files = select_files(dir_path)
        for form, (problem_path, answer_path) in files.items():
            if problem_path is None:
                continue
            answers = parse_answer_key(answer_path)
            parsed = parse_problem(problem_path, answers)
            flat = build_flat(year, month, exam_type, form, parsed)
            out_name = f"{year}_{month:02d}_{exam_type}_{form}.json"
            out_path = OUT_DIR / out_name
            out_path.write_text(
                json.dumps(flat, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            count += 1
            print(f"Wrote {out_path}")
    print(f"Done. {count} JSON file(s) written to {OUT_DIR}")


if __name__ == "__main__":
    main()
