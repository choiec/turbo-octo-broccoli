from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.crud.english.inventory import lexis_item
from app.crud.english.inventory import lexis_set as lexis_set_crud
from app.schemas.english.inventory.grammar_set import LexisSetMeta

router = APIRouter(prefix="/lexis/set", tags=["inventory_lexis_set"])


@router.get("", response_model=list[LexisSetMeta])
def list_lexis_sets(
    session: Session = Depends(get_session),
    _: dict[str, object] = Depends(verify_token),
) -> list[LexisSetMeta]:
    return lexis_set_crud.list_all(session)


@router.get(
    "/{set_id}",
    response_model=list[lexis_item.LexisItemSchema]
    | list[lexis_item.LexisItemWithProfile],
)
def get_lexis_set_items(
    set_id: str,
    with_profile: bool = False,
    session: Session = Depends(get_session),
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[lexis_item.LexisItemSchema] | list[lexis_item.LexisItemWithProfile]:
    item_ids = lexis_set_crud.list_by_lexis_set(session, set_id)
    if with_profile:
        return lexis_item.list_by_item_ids_with_profile(graph, item_ids)
    return lexis_item.list_by_item_ids(graph, item_ids)
