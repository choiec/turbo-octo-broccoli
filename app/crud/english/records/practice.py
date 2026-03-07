from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.practice import Practice, PracticeCreate


def create_practice(session: Session, body: PracticeCreate) -> Practice:
    row = Practice.model_validate(body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def list_practice(session: Session, learner_id: str) -> list[Practice]:
    return list(
        session.exec(
            select(Practice).where(Practice.learner_id == learner_id)
        ).all()
    )
