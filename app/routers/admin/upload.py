"""Admin CSV upload: lexis, grammar, testlet. Access via Cloudflare only."""

from __future__ import annotations

import tempfile
from pathlib import Path

import falkordb
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.scripts.init_english_profile import (
    init_grammar_profile,
    init_lexis_profile,
)
from app.scripts.init_testlet import init_from_csv

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
    """Upload CSV to load lexis profile into FalkorDB and SQLite."""
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
        finally:
            path.unlink(missing_ok=True)
    return {"uploaded": len(results), "results": results}


@router.post("/grammar")
def upload_grammar(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload CSV to load grammar profile into FalkorDB and SQLite."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            rows = init_grammar_profile(graph, session, path=path)
            results.append(
                {
                    "filename": upload.filename or "grammar.csv",
                    "rows_loaded": rows,
                }
            )
        finally:
            path.unlink(missing_ok=True)
    return {"uploaded": len(results), "results": results}


@router.post("/testlet")
def upload_testlet(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload questions CSV to load Source (SQLite) and Testlet (FalkorDB)."""
    results: list[dict] = []
    for upload in files:
        path = _save_upload_to_temp(upload)
        try:
            sources, testlets = init_from_csv(
                path, session, graph, dry_run=False
            )
            results.append(
                {
                    "filename": upload.filename or "questions.csv",
                    "sources": sources,
                    "testlets": testlets,
                }
            )
        finally:
            path.unlink(missing_ok=True)
    return {"uploaded": len(results), "results": results}
