from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import CefrLevel


class WritingAssessmentBase(SQLModel):
    learner_id: str = Field(index=True)
    session_at: datetime = Field(index=True)
    task_ref: str | None = Field(default=None)
    content: int
    grammar: int
    lexis: int
    organization: int
    english_total: int
    cefr_writing: CefrLevel | None = Field(default=None)
    feedback_text: str | None = Field(default=None)
    answer_text: str | None = Field(default=None)


class WritingAssessment(WritingAssessmentBase, table=True):
    __tablename__ = "writing_assessment"
    id: int | None = Field(default=None, primary_key=True)


class WritingAssessmentCreate(WritingAssessmentBase):
    pass


class WritingAssessmentRead(WritingAssessmentBase):
    id: int
