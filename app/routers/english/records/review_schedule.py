from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import learner_item as crud
from app.models.english.learner_item import LearnerItem
from app.schemas.english.records.learner_item import ReviewScheduleRead

router = APIRouter(prefix="/review-schedule", tags=["review-schedule"])


def _to_read(row: LearnerItem) -> ReviewScheduleRead:
    return ReviewScheduleRead(
        id=row.id,  # type: ignore[arg-type]
        learner_id=row.learner_id,
        task_item_id=row.item_id,
        card_state=row.fsrs_state,
        stability=row.stability,
        difficulty=row.difficulty,
        due_date=row.due_date,
        retrievability=row.retrievability,
    )


class ReviewScheduleUpsertBody(SQLModel):
    learner_id: str
    task_item_id: str
    response_rating: int  # 1=Again, 2=Hard, 3=Good, 4=Easy


@router.get("/due/{learner_id}", response_model=list[ReviewScheduleRead])
def list_due_items(
    learner_id: str,
    as_of: datetime | None = None,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[ReviewScheduleRead]:
    return [
        _to_read(r) for r in crud.list_due_items(session, learner_id, as_of)
    ]


@router.get("/{learner_id}", response_model=list[ReviewScheduleRead])
def list_review_schedule(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[ReviewScheduleRead]:
    return [_to_read(r) for r in crud.list_review_schedule(session, learner_id)]


@router.post("", response_model=ReviewScheduleRead)
def upsert_review_schedule(
    body: ReviewScheduleUpsertBody,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> ReviewScheduleRead:
    row = crud.upsert_review_schedule(
        session,
        body.learner_id,
        body.task_item_id,
        body.response_rating,
    )
    return _to_read(row)
