from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import CefrLevel, Skill


class LearnerProficiencyBase(SQLModel):
    learner_id: str = Field(index=True)
    skill: Skill
    cefr_level: CefrLevel
    assessed_at: datetime | None = Field(default=None)


class LearnerProficiency(LearnerProficiencyBase, table=True):
    __tablename__ = "learner_proficiency"
    id: int | None = Field(default=None, primary_key=True)


class LearnerProficiencyCreate(LearnerProficiencyBase):
    pass


class LearnerProficiencyRead(LearnerProficiencyBase):
    id: int


class LearnerProficiencyUpdate(SQLModel):
    cefr_level: CefrLevel | None = None
    assessed_at: datetime | None = None
