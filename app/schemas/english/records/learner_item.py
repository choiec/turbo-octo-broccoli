from __future__ import annotations

from datetime import datetime

from sqlmodel import SQLModel


class ReviewScheduleRead(SQLModel):
    """Response shape for /review-schedule (task_item)."""

    id: int
    learner_id: str
    task_item_id: str
    card_state: str | None
    stability: float
    difficulty: float
    due_date: datetime
    retrievability: float | None


class LexisReviewScheduleRead(SQLModel):
    """Response shape for /lexis-review-schedule (lexis)."""

    id: int
    learner_id: str
    item_id: str
    card_state: str | None
    stability: float
    difficulty: float
    due_date: datetime
    retrievability: float | None
