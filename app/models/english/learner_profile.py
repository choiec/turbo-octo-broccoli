from __future__ import annotations

from sqlmodel import Field, SQLModel

from app.models.english.enums import CefrLevel, GradeTag


class LearnerProfileBase(SQLModel):
    learner_id: str = Field(unique=True, index=True)
    name: str
    cefr_level: CefrLevel
    grade_tag: GradeTag
    schedule_days: str  # JSON array e.g. ["mon","wed","fri"]
    session_count: int = Field(default=0)


class LearnerProfile(LearnerProfileBase, table=True):
    __tablename__ = "learner_profile"
    id: int | None = Field(default=None, primary_key=True)


class LearnerProfileCreate(LearnerProfileBase):
    pass


class LearnerProfileRead(LearnerProfileBase):
    id: int
