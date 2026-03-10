from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.falkordb import get_graph_conn
from app.crud.english.inventory import task as task_crud
from app.crud.english.inventory import task_item as task_item_crud
from app.schemas.english.inventory.task import TaskParagraph
from app.schemas.english.inventory.task_item import TaskItem

router = APIRouter(prefix="/task", tags=["inventory_task"])


@router.get("/{task_id}/items", response_model=list[TaskItem])
def list_task_items(
    task_id: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[TaskItem]:
    """Return task items (questions) for the given task."""
    return task_item_crud.list_by_task(graph, task_id)


@router.get("/{cefr}", response_model=list[TaskParagraph])
def list_tasks_by_cefr(
    cefr: str,
    graph: falkordb.Graph = Depends(get_graph_conn),
    _: dict[str, object] = Depends(verify_token),
) -> list[TaskParagraph]:
    """Return task paragraphs whose lexis_cefr or grammar_cefr matches the CEFR level."""
    return task_crud.list_by_cefr(graph, cefr)
