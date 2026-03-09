from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import SessionType


class LessonLogBase(SQLModel):
    learner_id: str = Field(index=True)
    session_type: SessionType
    started_at: datetime
    ended_at: datetime | None = Field(default=None)


class LessonLog(LessonLogBase, table=True):
    __tablename__ = "lesson_log"
    id: int | None = Field(default=None, primary_key=True)


class LessonLogCreate(LessonLogBase):
    pass


class LessonLogRead(LessonLogBase):
    id: int
