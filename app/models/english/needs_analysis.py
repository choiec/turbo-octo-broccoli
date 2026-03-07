from __future__ import annotations

from sqlmodel import Field, SQLModel

from app.models.english.enums import CefrLevel, EnglishSystem, Skill


class NeedsAnalysisBase(SQLModel):
    cefr_level: CefrLevel
    english_skill: Skill | None = Field(default=None)
    english_system: EnglishSystem | None = Field(default=None)
    skill_weight: float


class NeedsAnalysis(NeedsAnalysisBase, table=True):
    __tablename__ = "needs_analysis"
    id: int | None = Field(default=None, primary_key=True)


class NeedsAnalysisRead(NeedsAnalysisBase):
    id: int
