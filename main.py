from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.falkordb import (
    GraphDbUnavailableError,
    get_graph_conn,
    init_graph_schema,
)
from app.core.seed_inventory import seed_grammar_lexis
from app.core.sqlite import engine
from app.routers import english


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    try:
        init_graph_schema()
        graph = next(get_graph_conn())
        seed_grammar_lexis(graph)
    except GraphDbUnavailableError as e:
        logging.warning("FalkorDB unavailable at startup: %s", e)
    yield


app = FastAPI(title="learner-portfolio", lifespan=lifespan)


@app.exception_handler(GraphDbUnavailableError)
def handle_graph_db_unavailable(
    _request: object, exc: GraphDbUnavailableError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)},
    )


app.include_router(english.router)
