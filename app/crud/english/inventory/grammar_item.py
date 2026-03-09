from __future__ import annotations

import json

from sqlmodel import Session, col, select

from app.models.english.grammar_item import GrammarItem, GrammarItemRead


def _to_read(row: GrammarItem) -> GrammarItemRead:
    return GrammarItemRead(
        id=row.id,  # type: ignore[arg-type]
        curriculum_id=row.curriculum_id,
        session_number=row.session_number,
        topic=row.topic,
        book_units=json.loads(row.book_units or "[]"),
    )


def upsert(
    session: Session,
    *,
    curriculum_id: str,
    session_number: int,
    topic: str,
    book_units: list[str],
) -> None:
    """Create or update a grammar item session. Idempotent."""
    existing = session.exec(
        select(GrammarItem).where(
            GrammarItem.curriculum_id == curriculum_id,
            GrammarItem.session_number == session_number,
        )
    ).first()
    units_json = json.dumps(book_units)
    if existing:
        existing.topic = topic
        existing.book_units = units_json
        session.add(existing)
    else:
        session.add(
            GrammarItem(
                curriculum_id=curriculum_id,
                session_number=session_number,
                topic=topic,
                book_units=units_json,
            )
        )
    session.commit()


def list_by_curriculum(
    session: Session, curriculum_id: str
) -> list[GrammarItemRead]:
    rows = session.exec(
        select(GrammarItem)
        .where(GrammarItem.curriculum_id == curriculum_id)
        .order_by(col(GrammarItem.session_number))
    ).all()
    return [_to_read(r) for r in rows]


def get(
    session: Session,
    curriculum_id: str,
    session_number: int,
) -> GrammarItemRead | None:
    row = session.exec(
        select(GrammarItem).where(
            GrammarItem.curriculum_id == curriculum_id,
            GrammarItem.session_number == session_number,
        )
    ).first()
    return _to_read(row) if row else None
