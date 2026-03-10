from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.crud.english.inventory import curriculum as crud
from app.crud.english.inventory.grammar import GrammarProfile
from app.schemas.english.inventory.curriculum import GrammarItemRead
from app.services.english.grammar_session import list_profiles_for_session

router = APIRouter(prefix="/grammar-items", tags=["inventory_grammar_item"])


@router.get(
    "/{curriculum_id}",
    response_model=list[GrammarItemRead],
)
def list_sessions(
    curriculum_id: str,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarItemRead]:
    return crud.list_by_curriculum(session, curriculum_id)


@router.get(
    "/{curriculum_id}/{session_number}",
    response_model=GrammarItemRead,
)
def get_session(
    curriculum_id: str,
    session_number: int,
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> GrammarItemRead:
    item = crud.get(session, curriculum_id, session_number)
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.get(
    "/{curriculum_id}/{session_number}/profiles",
    response_model=list[GrammarProfile],
)
def list_session_profiles(
    curriculum_id: str,
    session_number: int,
    session: Session = Depends(get_session),
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarProfile]:
    """Return GrammarProfiles to study for this curriculum session."""
    item = crud.get(session, curriculum_id, session_number)
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return list_profiles_for_session(
        curriculum_id, session_number, session, graph
    )
