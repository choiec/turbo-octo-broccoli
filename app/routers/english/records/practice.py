from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import practice as crud
from app.models.english.practice import PracticeCreate, PracticeRead

router = APIRouter(prefix="/practice", tags=["practice"])


@router.post("", response_model=PracticeRead)
def create_practice(
    body: PracticeCreate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> PracticeRead:
    return crud.create_practice(session, body)  # type: ignore[return-value]


@router.get("/{learner_id}", response_model=list[PracticeRead])
def list_practice(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[PracticeRead]:
    return crud.list_practice(session, learner_id)  # type: ignore[return-value]
