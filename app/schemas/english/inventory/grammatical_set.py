from __future__ import annotations

from pydantic import BaseModel


class GrammaticalSetMeta(BaseModel):
    """Metadata for a single grammatical set (textbook TOC entry)."""

    set_id: str
    source: str
    unit_num: int
    title: str | None = None
