from __future__ import annotations

from sqlmodel import Field, SQLModel


class GrammarProfile(SQLModel, table=True):
    __tablename__ = "grammar_profile"
    guideword: str = Field(primary_key=True)
    can_do: str | None = None
    example: str | None = None
    lexical_range: str | None = None
