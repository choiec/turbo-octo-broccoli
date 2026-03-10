from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.crud.english.inventory import grammar as grammar_crud
from app.crud.english.inventory import grammar_set as grammar_set_crud
from app.schemas.english.inventory.grammar_set import GrammarSetMeta

router = APIRouter(prefix="/grammar/set", tags=["inventory_grammar_set"])


@router.get("", response_model=list[GrammarSetMeta])
def list_grammar_sets(
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarSetMeta]:
    return grammar_set_crud.list_all(session)


@router.get("/{set_id}", response_model=list[grammar_crud.GrammarProfile])
def get_grammar_set_items(
    set_id: str,
    session: Session = Depends(get_session),
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[grammar_crud.GrammarProfile]:
    guidewords = grammar_set_crud.list_by_grammar_set(session, set_id)
    return grammar_crud.list_by_guidewords(graph, guidewords)
