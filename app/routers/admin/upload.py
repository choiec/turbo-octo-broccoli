"""Admin CSV upload: lexis, grammar, task. Access via Cloudflare only."""

from __future__ import annotations

import tempfile
from pathlib import Path

import falkordb
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import Session

from app.core.config import settings
from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.scripts.init_english_profile import (
    init_grammar_profile,
    init_lexis_profile,
)
from app.scripts.init_grammar_item import (
    init_from_json as init_grammar_item_from_json,
)
from app.scripts.init_grammar_unit import (
    init_from_json as init_grammar_unit_from_json,
)
from app.scripts.init_lexis_item import (
    init_from_json as init_lexis_item_from_json,
)
from app.scripts.init_task import init_from_json
from app.scripts.tag_grammar import tag_tasks

router = APIRouter()

_UPLOAD_HTML_PATH = Path(__file__).resolve().parent / "upload.html"


@router.get("", response_class=HTMLResponse)
def upload_page() -> str:
    """Serve upload form (GET). POST endpoints require Bearer token."""
    return _UPLOAD_HTML_PATH.read_text(encoding="utf-8")


def _save_upload_to_temp(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "upload").suffix or ".csv"
    fd = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = upload.file.read()
        fd.write(content)
        fd.close()
        return Path(fd.name)
    except Exception:
        fd.close()
        Path(fd.name).unlink(missing_ok=True)
        raise


@router.post("/lexis")
def upload_lexis(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload CSV: lexis profile into FalkorDB; per-corpus freq into SQLite."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
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


@router.post("/grammar")
def upload_grammar(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
):
    """Upload CSV: grammar profile into FalkorDB (all fields as node props)."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            rows = init_grammar_profile(graph, path=path)
            results.append(
                {
                    "filename": upload.filename or "grammar.csv",
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
):
    """Upload lexis-*.json to load LexicalSet and LexisItem (FalkorDB)."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            n_lists, n_items = init_lexis_item_from_json(
                path, graph, dry_run=False
            )
            results.append(
                {
                    "filename": upload.filename or "lexis.json",
                    "lexical_sets": n_lists,
                    "lexis_items": n_items,
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


@router.post("/grammar-unit")
def upload_grammar_unit(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
):
    """Upload grammar-*.json to load GrammaticalSet and GrammarProfile."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            n_sets, n_items = init_grammar_unit_from_json(
                path, graph, dry_run=False
            )
            results.append(
                {
                    "filename": upload.filename or "grammar.json",
                    "grammatical_sets": n_sets,
                    "grammar_links": n_items,
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


@router.post("/grammar-item")
def upload_grammar_item(
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
):
    """Upload grammar_outlines.json to load GrammarItem rows (SQLite)."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            n_sessions = init_grammar_item_from_json(path, session)
            results.append(
                {
                    "filename": upload.filename or "grammar_outlines.json",
                    "sessions_upserted": n_sessions,
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


@router.post("/task")
def upload_task(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload flat JSON to load Source (SQLite) and Task (FalkorDB)."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            sources, tasks, tagged_list = init_from_json(
                path, session, graph, dry_run=False
            )
            grammar_links = tag_tasks(
                graph,
                tagged_list,
                grammar_csv_path=None,
                openai_api_key=settings.openai_api_key or "",
            )
            results.append(
                {
                    "filename": upload.filename or "questions.json",
                    "sources": sources,
                    "tasks": tasks,
                    "grammar_links": grammar_links,
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
