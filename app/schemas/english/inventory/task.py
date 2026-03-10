from __future__ import annotations

from pydantic import BaseModel


class Task(BaseModel):
    """Response schema for a single task (inventory list)."""

    task_id: str
    source_id: str
    question_group: str
    lexis_cefr: str | None = None
    grammar_cefr: str | None = None
