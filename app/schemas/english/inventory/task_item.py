from __future__ import annotations

from pydantic import BaseModel


class TaskItem(BaseModel):
    """Response schema for a single task item."""

    task_item_id: str
    number: int
    section: str
    question_type: str
    stem: str
    options: list[str]
    answer: int
    score: int
