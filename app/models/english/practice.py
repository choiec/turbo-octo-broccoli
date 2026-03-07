from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import CefrLevel, EnglishSystem


class PracticeBase(SQLModel):
    learner_id: str = Field(index=True)
    domain: EnglishSystem
    item: str
    arpabet_ref: str | None = Field(default=None)
    cefr_level: CefrLevel | None = Field(default=None)
    practiced_at: datetime | None = Field(default=None)


class Practice(PracticeBase, table=True):
    __tablename__ = "english_practice"
    id: int | None = Field(default=None, primary_key=True)


class PracticeCreate(PracticeBase):
    pass


class PracticeRead(PracticeBase):
    id: int
