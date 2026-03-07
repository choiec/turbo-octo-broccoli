from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.sqlite import get_session
from app.crud.english.records import acquisition as crud
from app.models.english.acquisition import (
    AcquisitionCreate,
    AcquisitionRead,
    AcquisitionUpdate,
)

router = APIRouter(prefix="/acquisition", tags=["acquisition"])


@router.get("/{learner_id}", response_model=list[AcquisitionRead])
def list_acquisition(
    learner_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[AcquisitionRead]:
    return crud.list_acquisition(session, learner_id)  # type: ignore[return-value]


@router.post("", response_model=AcquisitionRead)
def create_acquisition(
    body: AcquisitionCreate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> AcquisitionRead:
    return crud.create_acquisition(session, body)  # type: ignore[return-value]


@router.put("/{acquisition_id}", response_model=AcquisitionRead)
def update_acquisition(
    acquisition_id: int,
    body: AcquisitionUpdate,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> AcquisitionRead:
    try:
        return crud.update_acquisition(session, acquisition_id, body)  # type: ignore[return-value]
    except ValueError:
        raise HTTPException(status_code=404, detail="not found")
