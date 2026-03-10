"""LexisSet (SQLite): textbook TOC index for LexisItem item_ids."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.grammar_set import LexisSet, LexisSetItem
from app.schemas.english.inventory.grammar_set import LexisSetMeta


def upsert_lexis_set(
    session: Session,
    *,
    set_id: str,
    source: str,
    unit_num: int,
) -> None:
    """Create or update LexisSet row. Idempotent."""
    row = session.exec(
        select(LexisSet).where(LexisSet.set_id == set_id)
    ).first()
    if row is None:
        row = LexisSet(set_id=set_id, source=source, unit_num=unit_num)
        session.add(row)
        session.flush()
    else:
        row.source = source
        row.unit_num = unit_num
        session.add(row)


def link_item(
    session: Session,
    *,
    set_id: str,
    item_id: str,
) -> None:
    """Add item_id to LexisSet. Idempotent."""
    existing = session.exec(
        select(LexisSetItem).where(
            LexisSetItem.set_id == set_id,
            LexisSetItem.item_id == item_id,
        )
    ).first()
    if existing is None:
        session.add(LexisSetItem(set_id=set_id, item_id=item_id))


def list_all(session: Session) -> list[LexisSetMeta]:
    """Return all LexisSet rows."""
    rows = session.exec(select(LexisSet).order_by(LexisSet.set_id)).all()
    return [
        LexisSetMeta(set_id=r.set_id, source=r.source, unit_num=r.unit_num)
        for r in rows
    ]


def list_by_lexis_set(session: Session, set_id: str) -> list[str]:
    """Return item_ids in the given LexisSet."""
    rows = session.exec(
        select(LexisSetItem.item_id).where(LexisSetItem.set_id == set_id)
    ).all()
    return list(rows)
