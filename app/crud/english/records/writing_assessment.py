from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.writing_assessment import (
    WritingAssessment,
    WritingAssessmentCreate,
)


def create_writing_assessment(
    session: Session, body: WritingAssessmentCreate
) -> WritingAssessment:
    row = WritingAssessment.model_validate(body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def list_writing_assessments(
    session: Session, learner_id: str
) -> list[WritingAssessment]:
    return list(
        session.exec(
            select(WritingAssessment).where(
                WritingAssessment.learner_id == learner_id
            )
        ).all()
    )
