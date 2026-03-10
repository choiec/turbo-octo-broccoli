from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.recall_event import (
    RecallEvent,
    RecallEventCreate,
)


def create_recall_event(
    session: Session, body: RecallEventCreate
) -> RecallEvent:
    row = RecallEvent.model_validate(body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def list_unprocessed_recall_events(session: Session) -> list[RecallEvent]:
    return list(
        session.exec(
            select(RecallEvent).where(RecallEvent.processed == False)
        ).all()
    )


def mark_processed(session: Session, event_id: int) -> RecallEvent:
    row = session.get(RecallEvent, event_id)
    if not row:
        raise ValueError(f"RecallEvent {event_id} not found")
    row.processed = True
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
