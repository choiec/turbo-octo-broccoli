from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import RecallSource


class ResponseLogBase(SQLModel):
    learner_id: str = Field(index=True)
    task_item_id: str = Field(index=True)
    answer: str
    correct: bool
    duration_sec: int | None = Field(default=None)
    source: RecallSource
    responded_at: datetime


class ResponseLog(ResponseLogBase, table=True):
    __tablename__ = "response_log"
    id: int | None = Field(default=None, primary_key=True)


class ResponseLogCreate(ResponseLogBase):
    pass


class ResponseLogRead(ResponseLogBase):
    id: int
