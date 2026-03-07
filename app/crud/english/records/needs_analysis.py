from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.enums import CefrLevel
from app.models.english.needs_analysis import NeedsAnalysis


def list_needs_analysis(
    session: Session, cefr_level: CefrLevel | None = None
) -> list[NeedsAnalysis]:
    query = select(NeedsAnalysis)
    if cefr_level:
        query = query.where(NeedsAnalysis.cefr_level == cefr_level)
    return list(session.exec(query).all())
