from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.learner_proficiency import (
    LearnerProficiency,
    LearnerProficiencyCreate,
    LearnerProficiencyUpdate,
)


def list_learner_proficiency(
    session: Session, learner_id: str
) -> list[LearnerProficiency]:
    return list(
        session.exec(
            select(LearnerProficiency).where(
                LearnerProficiency.learner_id == learner_id
            )
        ).all()
    )


def create_learner_proficiency(
    session: Session, body: LearnerProficiencyCreate
) -> LearnerProficiency:
    row = LearnerProficiency.model_validate(body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_learner_proficiency(
    session: Session,
    proficiency_id: int,
    body: LearnerProficiencyUpdate,
) -> LearnerProficiency:
    row = session.get(LearnerProficiency, proficiency_id)
    if not row:
        raise ValueError(f"LearnerProficiency {proficiency_id} not found")
    row.sqlmodel_update(body.model_dump(exclude_unset=True))
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
