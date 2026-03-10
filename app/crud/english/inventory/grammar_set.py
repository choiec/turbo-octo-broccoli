"""GrammarSet (SQLite): textbook TOC index for GrammarProfile guidewords."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.english.grammar_set import GrammarSet, GrammarSetItem
from app.schemas.english.inventory.grammar_set import GrammarSetMeta


def upsert_grammar_set(
    session: Session,
    *,
    set_id: str,
    source: str,
    unit_num: int,
    title: str | None = None,
) -> None:
    """Create or update GrammarSet row. Idempotent."""
    row = session.exec(
        select(GrammarSet).where(GrammarSet.set_id == set_id)
    ).first()
    if row is None:
        row = GrammarSet(
            set_id=set_id, source=source, unit_num=unit_num, title=title
        )
        session.add(row)
        session.flush()
    else:
        row.source = source
        row.unit_num = unit_num
        row.title = title
        session.add(row)


def link_grammar(
    session: Session,
    *,
    set_id: str,
    guideword: str,
) -> None:
    """Add guideword to GrammarSet. Idempotent."""
    existing = session.exec(
        select(GrammarSetItem).where(
            GrammarSetItem.set_id == set_id,
            GrammarSetItem.guideword == guideword,
        )
    ).first()
    if existing is None:
        session.add(GrammarSetItem(set_id=set_id, guideword=guideword))


def list_all(session: Session) -> list[GrammarSetMeta]:
    """Return all GrammarSet rows."""
    rows = session.exec(select(GrammarSet).order_by(GrammarSet.set_id)).all()
    return [
        GrammarSetMeta(
            set_id=r.set_id,
            source=r.source,
            unit_num=r.unit_num,
            title=r.title,
        )
        for r in rows
    ]


def list_by_grammar_set(session: Session, set_id: str) -> list[str]:
    """Return guidewords in the given GrammarSet."""
    rows = session.exec(
        select(GrammarSetItem.guideword).where(GrammarSetItem.set_id == set_id)
    ).all()
    return list(rows)
