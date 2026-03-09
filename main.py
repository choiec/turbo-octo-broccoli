from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.core.falkordb import (
    GraphDbUnavailableError,
    get_graph_conn,
    init_graph_schema,
    reset_graph,
)
from app.core.init_english_profile import (
    init_grammar_profile,
    init_lexis_profile,
)
from app.core.sqlite import engine
from app.models.english.grammar_profile import (  # noqa: F401
    GrammarProfile as GrammarProfileTable,
)
from app.models.english.lexis_profile import (  # noqa: F401
    LexisProfile as LexisProfileTable,
)
from app.routers import english


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    if settings.db_reset_on_startup:
        SQLModel.metadata.drop_all(engine)
        logging.warning("DB reset on startup: tables dropped")
    SQLModel.metadata.create_all(engine)
    try:
        if settings.db_reset_on_startup:
            reset_graph()
            logging.warning("DB reset on startup: FalkorDB graph dropped")
        init_graph_schema()
        graph = next(get_graph_conn())
        with Session(engine) as session:
            init_lexis_profile(graph, session)
            init_grammar_profile(graph, session)
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
