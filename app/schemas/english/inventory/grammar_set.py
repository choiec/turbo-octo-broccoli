from __future__ import annotations

from pydantic import BaseModel


class GrammarSetMeta(BaseModel):
    """Metadata for a single grammar set (textbook TOC entry)."""

    set_id: str
    source: str
    unit_num: int
    title: str | None = None


class LexisSetMeta(BaseModel):
    """Metadata for a single lexis set."""

    set_id: str
    source: str
    unit_num: int
