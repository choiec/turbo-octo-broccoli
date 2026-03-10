from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.crud.english.inventory.grammar import GrammarProfile
from app.crud.english.inventory.grammatical_set import (
    list_all,
    list_by_grammatical_set,
)
from app.schemas.english.inventory.grammatical_set import GrammaticalSetMeta

router = APIRouter(
    prefix="/grammatical-set", tags=["inventory_grammatical_set"]
)


@router.get("", response_model=list[GrammaticalSetMeta])
def list_grammatical_sets(
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammaticalSetMeta]:
    return list_all(graph)


@router.get("/{set_id}", response_model=list[GrammarProfile])
def get_grammatical_set_items(
    set_id: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarProfile]:
    return list_by_grammatical_set(graph, set_id)
