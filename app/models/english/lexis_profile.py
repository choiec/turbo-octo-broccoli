from __future__ import annotations

from sqlmodel import Field, SQLModel


class LexisProfile(SQLModel, table=True):
    __tablename__ = "lexis_profile"
    headword: str = Field(primary_key=True)
    corpus_name: str = Field(primary_key=True)
    cefr_level: str = Field(primary_key=True)
    freq: float
