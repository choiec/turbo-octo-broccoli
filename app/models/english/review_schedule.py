from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class ReviewScheduleBase(SQLModel):
    learner_id: str = Field(index=True)
    task_item_id: str = Field(index=True)
    stability: float
    difficulty: float
    due_date: datetime = Field(index=True)
    retrievability: float | None = Field(default=None)


class ReviewSchedule(ReviewScheduleBase, table=True):
    __tablename__ = "review_schedule"
    id: int | None = Field(default=None, primary_key=True)


class ReviewScheduleCreate(ReviewScheduleBase):
    pass


class ReviewScheduleRead(ReviewScheduleBase):
    id: int
