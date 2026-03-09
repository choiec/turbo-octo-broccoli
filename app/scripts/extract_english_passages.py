"""Extract English-only passages from temp/ 본문 text files into temp/english_only/."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_SRC = _ROOT / "temp"
_DEFAULT_OUT = _ROOT / "temp" / "english_only"


def _is_mostly_korean(line: str) -> bool:
    """Return True if non-empty line is 50% or more Korean by character count."""
    s = line.strip()
    if not s:
        return False
    korean_chars = sum(1 for c in s if "\uac00" <= c <= "\ud7a3")
    return korean_chars / len(s) >= 0.5


# Match "본문 2-1 – Title" or "본문 1 – Title" style section headers (drop entire line).
_RE_BONMUN_HEADING = re.compile(r"^\s*본문\s+[\d\-]+\s*[–\-]\s*.+$")


def _remove_korean_inline(text: str) -> str:
    """Remove trailing Korean (and adjacent spaces) on a line, e.g. '*word 한글뜻'."""
    return re.sub(r"[\uac00-\ud7a3\s]+$", "", text).rstrip()


def _is_bonmun_heading(line: str) -> bool:
    """Return True if line is a '본문 N-N – Title' style heading to drop."""
    return bool(_RE_BONMUN_HEADING.match(line.strip()))


def _process_line(line: str) -> str | None:
    """Return processed line or None to drop the line."""
    if _is_bonmun_heading(line):
        return None
    if _is_mostly_korean(line):
        return None
    cleaned = _remove_korean_inline(line)
    return cleaned if cleaned else None


def extract_english_lines(lines: list[str]) -> list[str]:
    """Process lines: drop mostly-Korean lines, strip inline Korean, collapse blank lines."""
    out: list[str] = []
    prev_blank = False
    for line in lines:
        processed = _process_line(line)
        if processed is None:
            if not prev_blank:
                out.append("")
                prev_blank = True
            continue
        prev_blank = False
        out.append(processed)
    # Trim trailing blank lines
    while out and out[-1] == "":
        out.pop()
    return out


def collect_passage_files(src: Path) -> list[Path]:
    """Return .txt files under src whose name contains '_본문'."""
    return sorted(
        p for p in src.rglob("*.txt") if "_본문" in p.name and p.is_file()
    )


def run(src: Path, out_root: Path, dry_run: bool) -> None:
    """Process all passage files under src and write to out_root."""
    files = collect_passage_files(src)
    if not files:
        print("No files with '_본문' in name found.", file=sys.stderr)
        return
    for fp in files:
        try:
            raw = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"Skip {fp}: {e}", file=sys.stderr)
            continue
        lines = raw.splitlines()
        result = extract_english_lines(lines)
        out_path = out_root / fp.relative_to(src)
        if dry_run:
            print(
                f"[dry-run] {fp.relative_to(_ROOT)} -> {out_path.relative_to(_ROOT)}"
            )
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            "\n".join(result) + ("\n" if result else ""), encoding="utf-8"
        )
    if not dry_run:
        print(f"Wrote {len(files)} file(s) under {out_root.relative_to(_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract English-only passages from temp/ 본문 text files."
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=_DEFAULT_SRC,
        help="Source directory to scan (default: temp/)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output root (default: temp/english_only/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list target files and output paths, do not write.",
    )
    args = parser.parse_args()
    src = (args.src if args.src.is_absolute() else _ROOT / args.src).resolve()
    out_root = args.out if args.out is not None else _DEFAULT_OUT
    out_root = (
        out_root if out_root.is_absolute() else _ROOT / out_root
    ).resolve()
    run(src, out_root, args.dry_run)


if __name__ == "__main__":
    main()
