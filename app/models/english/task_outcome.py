from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import EnglishSystem, Skill


class TaskOutcomeBase(SQLModel):
    learner_id: str = Field(index=True)
    session_at: datetime = Field(index=True)
    task_ref: str | None = Field(default=None)
    outcome_correct: bool | None = Field(default=None)
    answer_text: str | None = Field(default=None)
    skill: Skill | None = Field(default=None)
    system: EnglishSystem | None = Field(default=None)


class TaskOutcome(TaskOutcomeBase, table=True):
    __tablename__ = "task_outcome"
    id: int | None = Field(default=None, primary_key=True)


class TaskOutcomeCreate(TaskOutcomeBase):
    pass


class TaskOutcomeRead(TaskOutcomeBase):
    id: int
