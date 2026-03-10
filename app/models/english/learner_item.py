from __future__ import annotations

from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class LearnerItemBase(SQLModel):
    learner_id: str = Field(index=True)
    item_type: str = Field(index=True)  # "task_item" | "lexis"
    item_id: str = Field(index=True)
    fsrs_state: str | None = Field(default=None)  # FSRS Card as JSON
    stability: float
    difficulty: float
    due_date: datetime = Field(index=True)
    retrievability: float | None = Field(default=None)


class LearnerItem(LearnerItemBase, table=True):
    __tablename__ = "learner_item"
    __table_args__ = (UniqueConstraint("learner_id", "item_type", "item_id"),)
    id: int | None = Field(default=None, primary_key=True)
