from __future__ import annotations

import kuzu
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.kuzu import get_graph_conn
from app.crud.english.inventory.grammar import GrammarItem, list_by_cefr

router = APIRouter(prefix="/grammar", tags=["inventory_grammar"])


@router.get("/{cefr}", response_model=list[GrammarItem])
def list_grammar_by_cefr(
    cefr: str,
    conn: kuzu.Connection = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[GrammarItem]:
    return list_by_cefr(conn, cefr)
