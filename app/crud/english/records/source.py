from __future__ import annotations

from sqlmodel import Session

from app.models.english.source import Source


def upsert_source(
    session: Session,
    *,
    source_id: str,
    year: int | None = None,
    month: int | None = None,
    exam_type: str,
    academic_year: int | None = None,
    form: str | None = None,
    issuer: str = "KICE",
    source_type: str = "testlet",
) -> Source:
    """Create or update a Source row by source_id. Idempotent."""
    row = session.get(Source, source_id)
    if row:
        row.year = year
        row.month = month
        row.exam_type = exam_type
        row.academic_year = academic_year
        row.form = form
        row.issuer = issuer
        row.source_type = source_type
        session.add(row)
    else:
        row = Source(
            source_id=source_id,
            year=year,
            month=month,
            exam_type=exam_type,
            academic_year=academic_year,
            form=form,
            issuer=issuer,
            source_type=source_type,
        )
        session.add(row)
    session.commit()
    session.refresh(row)
    return row
