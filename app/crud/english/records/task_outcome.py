from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.task_outcome import TaskOutcome, TaskOutcomeCreate


def create_task_outcome(
    session: Session, body: TaskOutcomeCreate
) -> TaskOutcome:
    row = TaskOutcome.model_validate(body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def list_task_outcomes(session: Session, learner_id: str) -> list[TaskOutcome]:
    return list(
        session.exec(
            select(TaskOutcome).where(TaskOutcome.learner_id == learner_id)
        ).all()
    )
