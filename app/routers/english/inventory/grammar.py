from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.crud.english.inventory.grammar import GrammarProfile, list_by_cefr

router = APIRouter(prefix="/grammar", tags=["inventory_grammar"])


@router.get("/{cefr}", response_model=list[GrammarProfile])
def list_grammar_by_cefr(
    cefr: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarProfile]:
    return list_by_cefr(graph, cefr)
