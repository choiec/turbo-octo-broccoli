from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import needs_analysis as crud
from app.models.english.enums import CefrLevel
from app.models.english.needs_analysis import NeedsAnalysisRead

router = APIRouter(prefix="/needs-analysis", tags=["needs_analysis"])


@router.get("", response_model=list[NeedsAnalysisRead])
def list_needs_analysis(
    cefr_level: CefrLevel | None = None,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[NeedsAnalysisRead]:
    return crud.list_needs_analysis(session, cefr_level)  # type: ignore[return-value]
