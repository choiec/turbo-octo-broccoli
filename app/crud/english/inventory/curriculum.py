"""Curriculum: upsert session/units; re-export queries."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.curriculum import (
    Curriculum,
    CurriculumSession,
    CurriculumSessionUnit,
)
from app.schemas.english.inventory.curriculum import GrammarItemRead


def _replace_units(
    session: Session,
    session_id: int,
    book_units: list[str],
) -> None:
    """Delete existing CurriculumSessionUnits for session_id; add new ones."""
    for unit in session.exec(
        select(CurriculumSessionUnit).where(
            CurriculumSessionUnit.session_id == session_id
        )
    ).all():
        session.delete(unit)
    for set_id in book_units:
        session.add(
            CurriculumSessionUnit(
                session_id=session_id,
                set_id=set_id,
            )
        )


def upsert(
    session: Session,
    *,
    curriculum_id: str,
    session_number: int,
    topic: str,
    book_units: list[str],
) -> None:
    """Create or update a curriculum session. Idempotent."""
    curriculum = session.exec(
        select(Curriculum).where(Curriculum.curriculum_id == curriculum_id)
    ).first()
    if curriculum is None:
        curriculum = Curriculum(curriculum_id=curriculum_id)
        session.add(curriculum)
        session.flush()

    existing_session = session.exec(
        select(CurriculumSession).where(
            CurriculumSession.curriculum_id == curriculum_id,
            CurriculumSession.session_number == session_number,
        )
    ).first()
    if existing_session is None:
        existing_session = CurriculumSession(
            curriculum_id=curriculum_id,
            session_number=session_number,
            topic=topic,
        )
        session.add(existing_session)
        session.flush()
    else:
        existing_session.topic = topic
        session.add(existing_session)

    _replace_units(session, existing_session.id, book_units)  # type: ignore[arg-type]
    session.commit()


def _session_to_item(
    session: Session,
    s: CurriculumSession,
) -> GrammarItemRead:
    assert s.id is not None  # persisted row
    units = list(
        session.exec(
            select(CurriculumSessionUnit).where(
                CurriculumSessionUnit.session_id == s.id
            )
        ).all()
    )
    return GrammarItemRead(
        id=s.id,
        curriculum_id=s.curriculum_id,
        session_number=s.session_number,
        topic=s.topic,
        book_units=[u.set_id for u in units],
    )


def list_by_curriculum(
    session: Session,
    curriculum_id: str,
) -> list[GrammarItemRead]:
    """Return all curriculum sessions for the given curriculum_id."""
    sessions = list(
        session.exec(
            select(CurriculumSession)
            .where(CurriculumSession.curriculum_id == curriculum_id)
            .order_by(CurriculumSession.session_number)  # type: ignore[arg-type]
        ).all()
    )
    return [_session_to_item(session, s) for s in sessions]


def get(
    session: Session,
    curriculum_id: str,
    session_number: int,
) -> GrammarItemRead | None:
    """Return one curriculum session by curriculum_id and session_number."""
    s = session.exec(
        select(CurriculumSession).where(
            CurriculumSession.curriculum_id == curriculum_id,
            CurriculumSession.session_number == session_number,
        )
    ).first()
    if s is None:
        return None
    return _session_to_item(session, s)
