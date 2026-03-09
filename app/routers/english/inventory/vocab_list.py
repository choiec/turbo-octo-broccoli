from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.crud.english.inventory.lexis_item import (
    LexisItemSchema,
    list_by_vocab_list,
)
from app.crud.english.inventory.vocab_list import VocabListMeta, list_all

router = APIRouter(prefix="/vocab-list", tags=["inventory_vocab_list"])


@router.get("", response_model=list[VocabListMeta])
def list_vocab_lists(
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[VocabListMeta]:
    return list_all(graph)


@router.get("/{list_id}", response_model=list[LexisItemSchema])
def get_vocab_list_items(
    list_id: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[LexisItemSchema]:
    return list_by_vocab_list(graph, list_id)
