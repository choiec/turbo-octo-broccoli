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
from app.core.sqlite import engine
from app.models.common.concept import Concept  # noqa: F401
from app.models.common.link_type import LinkType  # noqa: F401
from app.models.common.object_type import ObjectType  # noqa: F401
from app.models.english.error_prior import ErrorPrior  # noqa: F401
from app.models.english.essay_outcome import EssayOutcome  # noqa: F401
from app.models.english.exam_period import (  # noqa: F401
    ExamPeriod,
    LearnerExamOverride,
)
from app.models.english.fsrs_config import FsrsConfig  # noqa: F401
from app.models.english.learner_profile import LearnerProfile  # noqa: F401
from app.models.english.lesson_log import LessonLog  # noqa: F401
from app.models.english.lexis_corpus_freq import (
    LexisCorpusFreq as _,  # noqa: F401
)
from app.models.english.question_log import QuestionLog  # noqa: F401
from app.models.english.recall_event import RecallEvent  # noqa: F401
from app.models.english.response_log import ResponseLog  # noqa: F401
from app.models.english.review_schedule import ReviewSchedule  # noqa: F401
from app.models.english.source import Source  # noqa: F401
from app.routers import admin, english


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    logging.info("db_reset_on_startup=%s", settings.db_reset_on_startup)
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
            from app.crud.english.inventory import cefr

            cefr.ensure_cefr_levels(graph, session)
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


app.include_router(admin.router)
app.include_router(english.router)
