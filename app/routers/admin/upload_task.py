"""Admin upload: task JSON and chunk JSON (Source, Task, TaskItem)."""

from __future__ import annotations

import falkordb
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.config import settings
from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.routers.admin._upload_helpers import (
    enqueue_tagging,
    save_upload_to_temp,
)
from app.scripts.init_chunk import init_from_json as init_chunk_from_json
from app.scripts.init_task import init_from_json
from app.scripts.tag_grammar import tag_tasks
from app.scripts.tag_lexis import tag_tasks as tag_lexis_tasks

router = APIRouter()


@router.post("/task")
def upload_task(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload flat JSON to load Source (SQLite) and Task (FalkorDB).

    Grammar tagging runs as a background task after the response is returned.
    """
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            sources, tasks, tagged_list = init_from_json(
                path, session, graph, dry_run=False
            )
            tagging = enqueue_tagging(background_tasks, graph, tagged_list)
            results.append(
                {
                    "filename": upload.filename or "questions.json",
                    "sources": sources,
                    "tasks": tasks,
                    "grammar_tagging": tagging,
                }
            )
        except Exception as e:
            path.unlink(missing_ok=True)
            return JSONResponse(
                status_code=500,
                content={"detail": str(e), "filename": upload.filename},
            )
        finally:
            path.unlink(missing_ok=True)
    return {"uploaded": len(results), "results": results}


@router.post("/chunk")
def upload_chunk(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload chunk JSON to load Source and Task.

    Grammar and lexis tagging run synchronously before the response.
    """
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            sources, tasks, tagged_list = init_chunk_from_json(
                path, session, graph, dry_run=False
            )
            n_links = tag_tasks(
                graph,
                tagged_list,
                grammar_csv_path=None,
                openai_api_key=settings.openai_api_key or "",
            )
            tag_lexis_tasks(graph, tagged_list)
            results.append(
                {
                    "filename": upload.filename or "chunks.json",
                    "sources": sources,
                    "tasks": tasks,
                    "grammar_links": n_links,
                }
            )
        except Exception as e:
            path.unlink(missing_ok=True)
            return JSONResponse(
                status_code=500,
                content={"detail": str(e), "filename": upload.filename},
            )
        finally:
            path.unlink(missing_ok=True)
    return {"uploaded": len(results), "results": results}
