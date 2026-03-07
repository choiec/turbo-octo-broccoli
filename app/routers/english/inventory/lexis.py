from __future__ import annotations

import kuzu
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.kuzu import get_graph_conn
from app.crud.english.inventory.lexis import LexisItem, list_by_cefr

router = APIRouter(prefix="/lexis", tags=["inventory_lexis"])


@router.get("/{cefr}", response_model=list[LexisItem])
def list_lexis_by_cefr(
    cefr: str,
    conn: kuzu.Connection = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[LexisItem]:
    return list_by_cefr(conn, cefr)
