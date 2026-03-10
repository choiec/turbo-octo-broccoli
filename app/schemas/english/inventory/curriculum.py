from __future__ import annotations

from sqlmodel import SQLModel


class GrammarItemRead(SQLModel):
    """API response schema for curriculum grammar item (projection)."""

    id: int
    curriculum_id: str
    session_number: int
    topic: str
    book_units: list[str]
