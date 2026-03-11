---
description: |
  Tool selection: when to use Shell vs. specialized tools (Read/Write/Grep/Glob).
alwaysApply: true
---

**§T (Tools)**: Prefer specialized tools over Shell. Use Shell only when no
dedicated tool exists for the task.

**Use Shell for:**
- Git operations (`git status`, `git add`, `git commit`, `git mv`, etc.)
- Build/type-check/test (`pytest`, `ruff check .`, `ruff format .`, `ty check`)
- Dependency install (`uv add`, `uv sync`)
- Rename/move files when content is unchanged — use `git mv` (per §R)
- Process/server management, environment checks

**Do not use Shell for these — use the dedicated tool:**

| Task           | Tool            |
|----------------|-----------------|
| Read file      | `Read`          |
| Create/write   | `Write`         |
| Edit in place  | `StrReplace`    |
| Text search    | `Grep`          |
| File by pattern| `Glob`          |
| Semantic search| `SemanticSearch`|

Do not run `find`, `grep`, `cat`, `head`, `tail`, `sed`, or `awk` in Shell;
use `Grep`, `Glob`, or `Read` instead.
