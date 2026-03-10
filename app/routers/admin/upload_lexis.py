"""Admin upload: lexis CSV and lexis JSON (LexisSet / LexisItem)."""

from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.routers.admin._upload_helpers import (
    save_upload_to_temp,
    upload_lexis_json,
)
from app.scripts.init_english_profile import init_lexis_profile
from app.scripts.init_lexis_item import (
    init_from_json as init_lexis_item_from_json,
)

router = APIRouter()


@router.post("/lexis")
def upload_lexis(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload CSV: lexis profile into FalkorDB; per-corpus freq into SQLite."""
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            rows = init_lexis_profile(graph, session, path=path)
            results.append(
                {
                    "filename": upload.filename or "lexis.csv",
                    "rows_loaded": rows,
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


@router.post("/lexis-item")
def upload_lexis_item(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload lexis-*.json: LexisItem (FalkorDB) and LexisSet (SQLite)."""
    return upload_lexis_json(
        files, graph, session, "lexis.json", init_lexis_item_from_json
    )


@router.post("/lexis-set")
def upload_lexis_set(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload lexis-*.json: LexisSet and LexisItem."""
    return upload_lexis_json(
        files, graph, session, "lexis.json", init_lexis_item_from_json
    )


@router.post("/lexis-oewn")
def upload_lexis_oewn(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload OEWN 2025 senses JSON (from fetch_oewn.py). LexisItem only, no LexisSet."""
    return upload_lexis_json(
        files,
        graph,
        session,
        "oewn_2025_senses.json",
        init_lexis_item_from_json,
    )
