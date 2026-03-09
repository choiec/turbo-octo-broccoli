from __future__ import annotations

from datetime import date

from sqlmodel import Field, SQLModel

from app.models.english.enums import ExamType, GradeTag


class ExamPeriodBase(SQLModel):
    grade_tag: GradeTag
    exam_type: ExamType
    semester: int
    exam_start: date
    exam_end: date


class ExamPeriod(ExamPeriodBase, table=True):
    __tablename__ = "exam_period"
    id: int | None = Field(default=None, primary_key=True)


class ExamPeriodCreate(ExamPeriodBase):
    pass


class ExamPeriodRead(ExamPeriodBase):
    id: int


class LearnerExamOverrideBase(SQLModel):
    learner_id: str = Field(index=True)
    exam_start: date
    exam_end: date


class LearnerExamOverride(LearnerExamOverrideBase, table=True):
    __tablename__ = "learner_exam_override"
    id: int | None = Field(default=None, primary_key=True)


class LearnerExamOverrideCreate(LearnerExamOverrideBase):
    pass


class LearnerExamOverrideRead(LearnerExamOverrideBase):
    id: int
