from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class EssayOutcomeBase(SQLModel):
    learner_id: str = Field(index=True)
    accuracy: float
    vocabulary: float
    coherence: float
    task_completion: float
    feedback: str | None = Field(default=None)
    assessed_at: datetime


class EssayOutcome(EssayOutcomeBase, table=True):
    __tablename__ = "essay_outcome"
    id: int | None = Field(default=None, primary_key=True)


class EssayOutcomeCreate(EssayOutcomeBase):
    pass


class EssayOutcomeRead(EssayOutcomeBase):
    id: int
