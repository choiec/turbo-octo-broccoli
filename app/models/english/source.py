from __future__ import annotations

from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    """Exam source metadata. Referenced by Testlet in FalkorDB via source_id."""

    __tablename__ = "english_source"
    source_id: str = Field(primary_key=True)
    year: int
    month: int
    exam_type: str
    academic_year: int
    form: str | None = Field(default=None)
    issuer: str = Field(default="KICE")
    source_type: str = Field(default="testlet")
