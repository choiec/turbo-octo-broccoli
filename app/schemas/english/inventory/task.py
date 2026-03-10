from __future__ import annotations

from pydantic import BaseModel


class TaskParagraph(BaseModel):
    """Response schema for a single task paragraph (inventory list)."""

    task_id: str
    source_id: str
    question_group: str
    lexis_cefr: str | None = None
    grammar_cefr: str | None = None
