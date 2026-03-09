from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class QuestionLogBase(SQLModel):
    learner_id: str = Field(index=True)
    item_id: str = Field(index=True)
    assigned_at: datetime
    due_date: datetime | None = Field(default=None)


class QuestionLog(QuestionLogBase, table=True):
    __tablename__ = "question_log"
    id: int | None = Field(default=None, primary_key=True)


class QuestionLogCreate(QuestionLogBase):
    pass


class QuestionLogRead(QuestionLogBase):
    id: int
