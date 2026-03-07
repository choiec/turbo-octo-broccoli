from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import learner_proficiency as crud
from app.models.english.learner_proficiency import (
    LearnerProficiencyCreate,
    LearnerProficiencyRead,
    LearnerProficiencyUpdate,
)

router = APIRouter(prefix="/learner-proficiency", tags=["learner_proficiency"])


@router.get("/{learner_id}", response_model=list[LearnerProficiencyRead])
def list_learner_proficiency(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[LearnerProficiencyRead]:
    return crud.list_learner_proficiency(session, learner_id)  # type: ignore[return-value]


@router.post("", response_model=LearnerProficiencyRead)
def create_learner_proficiency(
    body: LearnerProficiencyCreate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> LearnerProficiencyRead:
    return crud.create_learner_proficiency(session, body)  # type: ignore[return-value]


@router.put("/{proficiency_id}", response_model=LearnerProficiencyRead)
def update_learner_proficiency(
    proficiency_id: int,
    body: LearnerProficiencyUpdate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> LearnerProficiencyRead:
    try:
        return crud.update_learner_proficiency(  # type: ignore[return-value]
            session, proficiency_id, body
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="not found")
