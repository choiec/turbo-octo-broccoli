from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import task_outcome as crud
from app.models.english.task_outcome import TaskOutcomeCreate, TaskOutcomeRead

router = APIRouter(prefix="/task-outcome", tags=["task_outcome"])


@router.post("", response_model=TaskOutcomeRead)
def create_task_outcome(
    body: TaskOutcomeCreate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> TaskOutcomeRead:
    return crud.create_task_outcome(session, body)  # type: ignore[return-value]


@router.get("/{learner_id}", response_model=list[TaskOutcomeRead])
def list_task_outcomes(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[TaskOutcomeRead]:
    return crud.list_task_outcomes(session, learner_id)  # type: ignore[return-value]
