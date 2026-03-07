from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import writing_assessment as crud
from app.models.english.writing_assessment import (
    WritingAssessmentCreate,
    WritingAssessmentRead,
)

router = APIRouter(prefix="/writing-assessment", tags=["writing_assessment"])


@router.post("", response_model=WritingAssessmentRead)
def create_writing_assessment(
    body: WritingAssessmentCreate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> WritingAssessmentRead:
    return crud.create_writing_assessment(session, body)  # type: ignore[return-value]


@router.get("/{learner_id}", response_model=list[WritingAssessmentRead])
def list_writing_assessments(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[WritingAssessmentRead]:
    return crud.list_writing_assessments(session, learner_id)  # type: ignore[return-value]
