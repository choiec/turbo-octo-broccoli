from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.english.enums import CefrLevel, QuestionType


class ErrorPriorBase(SQLModel):
    cefr_level: CefrLevel
    question_type: QuestionType
    error_rate: float


class ErrorPrior(ErrorPriorBase, table=True):
    __tablename__ = "error_prior"
    __table_args__ = (UniqueConstraint("cefr_level", "question_type"),)
    id: int | None = Field(default=None, primary_key=True)


class ErrorPriorCreate(ErrorPriorBase):
    pass


class ErrorPriorRead(ErrorPriorBase):
    id: int
