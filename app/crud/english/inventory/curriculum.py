from __future__ import annotations

from sqlmodel import Session, col, select

from app.models.english.curriculum import (
    Curriculum,
    CurriculumSession,
    CurriculumSessionUnit,
)
from app.schemas.english.inventory.curriculum import GrammarItemRead


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

    for unit in session.exec(
        select(CurriculumSessionUnit).where(
            CurriculumSessionUnit.session_id == existing_session.id
        )
    ).all():
        session.delete(unit)
    for set_id in book_units:
        session.add(
            CurriculumSessionUnit(
                session_id=existing_session.id,  # type: ignore[arg-type]
                set_id=set_id,
            )
        )
    session.commit()


def list_by_curriculum(
    session: Session, curriculum_id: str
) -> list[GrammarItemRead]:
    rows = session.exec(
        select(CurriculumSession)
        .where(CurriculumSession.curriculum_id == curriculum_id)
        .order_by(col(CurriculumSession.session_number))
    ).all()
    result: list[GrammarItemRead] = []
    for row in rows:
        units = session.exec(
            select(CurriculumSessionUnit.set_id).where(
                CurriculumSessionUnit.session_id == row.id
            )
        ).all()
        result.append(
            GrammarItemRead(
                id=row.id,  # type: ignore[arg-type]
                curriculum_id=row.curriculum_id,
                session_number=row.session_number,
                topic=row.topic,
                book_units=list(units),
            )
        )
    return result


def get(
    session: Session,
    curriculum_id: str,
    session_number: int,
) -> GrammarItemRead | None:
    row = session.exec(
        select(CurriculumSession).where(
            CurriculumSession.curriculum_id == curriculum_id,
            CurriculumSession.session_number == session_number,
        )
    ).first()
    if row is None:
        return None
    units = session.exec(
        select(CurriculumSessionUnit.set_id).where(
            CurriculumSessionUnit.session_id == row.id
        )
    ).all()
    return GrammarItemRead(
        id=row.id,  # type: ignore[arg-type]
        curriculum_id=row.curriculum_id,
        session_number=row.session_number,
        topic=row.topic,
        book_units=list(units),
    )
