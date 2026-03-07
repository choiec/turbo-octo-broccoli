from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.acquisition import (
    Acquisition,
    AcquisitionCreate,
    AcquisitionUpdate,
)


def list_acquisition(session: Session, learner_id: str) -> list[Acquisition]:
    return list(
        session.exec(
            select(Acquisition).where(Acquisition.learner_id == learner_id)
        ).all()
    )


def create_acquisition(
    session: Session, body: AcquisitionCreate
) -> Acquisition:
    row = Acquisition.model_validate(body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_acquisition(
    session: Session,
    acquisition_id: int,
    body: AcquisitionUpdate,
) -> Acquisition:
    row = session.get(Acquisition, acquisition_id)
    if not row:
        raise ValueError(f"Acquisition {acquisition_id} not found")
    row.sqlmodel_update(body.model_dump(exclude_unset=True))
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
