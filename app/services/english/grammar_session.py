"""Resolve curriculum session to GrammarProfiles via GrammarSet (SQLite)."""

from __future__ import annotations

import falkordb
from sqlmodel import Session

from app.crud.english.inventory import curriculum as curriculum_crud
from app.crud.english.inventory import grammar as grammar_crud
from app.crud.english.inventory import grammar_set as grammar_set_crud
from app.crud.english.inventory.grammar import GrammarProfile


def list_profiles_for_session(
    curriculum_id: str,
    session_number: int,
    session: Session,
    graph: falkordb.Graph,
) -> list[GrammarProfile]:
    """Return GrammarProfiles to study for the given curriculum session."""
    item = curriculum_crud.get(session, curriculum_id, session_number)
    if not item:
        return []
    guidewords: list[str] = []
    for set_id in item.book_units:
        guidewords.extend(grammar_set_crud.list_by_grammar_set(session, set_id))
    return grammar_crud.list_by_guidewords(graph, guidewords)
