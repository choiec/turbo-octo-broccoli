from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Curriculum(SQLModel, table=True):
    __tablename__ = "curriculum"
    id: int | None = Field(default=None, primary_key=True)
    curriculum_id: str = Field(unique=True, index=True)


class CurriculumSession(SQLModel, table=True):
    __tablename__ = "curriculum_session"
    __table_args__ = (UniqueConstraint("curriculum_id", "session_number"),)
    id: int | None = Field(default=None, primary_key=True)
    curriculum_id: str = Field(
        foreign_key="curriculum.curriculum_id", index=True
    )
    session_number: int
    topic: str = ""

    units: list[CurriculumSessionUnit] = Relationship(back_populates="session")


class CurriculumSessionUnit(SQLModel, table=True):
    __tablename__ = "curriculum_session_unit"
    __table_args__ = (UniqueConstraint("session_id", "set_id"),)
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="curriculum_session.id", index=True)
    set_id: str = Field(index=True)  # GrammaticalSet.set_id (FalkorDB)

    session: CurriculumSession | None = Relationship(back_populates="units")
