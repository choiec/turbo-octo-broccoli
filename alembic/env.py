from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from app.models.common.concept import Concept  # noqa: F401
from app.models.common.link_type import LinkType  # noqa: F401
from app.models.common.object_type import ObjectType  # noqa: F401
from app.models.english.acquisition import Acquisition  # noqa: F401
from app.models.english.curriculum import (  # noqa: F401
    Curriculum,
    CurriculumSession,
    CurriculumSessionUnit,
)
from app.models.english.error_prior import ErrorPrior  # noqa: F401
from app.models.english.essay_outcome import EssayOutcome  # noqa: F401
from app.models.english.exam_period import (  # noqa: F401
    ExamPeriod,
    LearnerExamOverride,
)
from app.models.english.fsrs_config import FsrsConfig  # noqa: F401
from app.models.english.grammar_set import (  # noqa: F401
    GrammarSet,
    GrammarSetItem,
    LexisSet,
    LexisSetItem,
)
from app.models.english.learner_item import LearnerItem  # noqa: F401
from app.models.english.learner_proficiency import (
    LearnerProficiency,  # noqa: F401
)
from app.models.english.learner_profile import LearnerProfile  # noqa: F401
from app.models.english.lesson_log import LessonLog  # noqa: F401
from app.models.english.lexis_corpus_freq import (  # noqa: F401
    LexisCorpusFreq as _,
)
from app.models.english.needs_analysis import NeedsAnalysis  # noqa: F401
from app.models.english.practice import Practice  # noqa: F401
from app.models.english.question_log import QuestionLog  # noqa: F401
from app.models.english.recall_event import RecallEvent  # noqa: F401
from app.models.english.response_log import ResponseLog  # noqa: F401
from app.models.english.source import Source  # noqa: F401
from app.models.english.task_outcome import TaskOutcome  # noqa: F401
from app.models.english.writing_assessment import (
    WritingAssessment,  # noqa: F401
)

config = context.config
# CLI: use env; app (command.upgrade): url set in main
_url = config.get_main_option("sqlalchemy.url")
if not _url or _url.startswith("driver:"):
    _path = os.getenv("SQLITE_PATH", "./learner_portfolio.db")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{_path}")
target_metadata = SQLModel.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    section = config.get_section(config.config_ini_section, {})
    _online_url = config.get_main_option("sqlalchemy.url")
    section["sqlalchemy.url"] = _online_url or "sqlite:///"
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
