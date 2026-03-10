"""GrammarSet and LexisSet (SQLite): textbook TOC for grammar and lexis."""

from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class GrammarSet(SQLModel, table=True):
    __tablename__ = "grammar_set"
    id: int | None = Field(default=None, primary_key=True)
    set_id: str = Field(unique=True, index=True)
    source: str = ""
    unit_num: int = 0
    title: str | None = None

    items: list[GrammarSetItem] = Relationship(back_populates="set_row")


class GrammarSetItem(SQLModel, table=True):
    __tablename__ = "grammar_set_item"
    __table_args__ = (UniqueConstraint("set_id", "guideword"),)
    id: int | None = Field(default=None, primary_key=True)
    set_id: str = Field(foreign_key="grammar_set.set_id", index=True)
    guideword: str = Field(index=True)

    set_row: GrammarSet | None = Relationship(back_populates="items")


class LexisSet(SQLModel, table=True):
    __tablename__ = "lexis_set"
    id: int | None = Field(default=None, primary_key=True)
    set_id: str = Field(unique=True, index=True)
    source: str = ""
    unit_num: int = 0

    items: list[LexisSetItem] = Relationship(back_populates="set_row")


class LexisSetItem(SQLModel, table=True):
    __tablename__ = "lexis_set_item"
    __table_args__ = (UniqueConstraint("set_id", "item_id"),)
    id: int | None = Field(default=None, primary_key=True)
    set_id: str = Field(foreign_key="lexis_set.set_id", index=True)
    item_id: str = Field(index=True)

    set_row: LexisSet | None = Relationship(back_populates="items")
