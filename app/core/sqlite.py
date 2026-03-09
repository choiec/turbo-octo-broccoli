from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    connect_args={"check_same_thread": False},
)


def auto_migrate(eng: Engine) -> None:
    """Add missing columns to existing tables (SQLite ADD COLUMN only)."""
    inspector = inspect(eng)
    existing_tables = set(inspector.get_table_names())
    with eng.connect() as conn:
        for table_name, table in SQLModel.metadata.tables.items():
            if table_name not in existing_tables:
                continue
            existing_cols = {
                c["name"] for c in inspector.get_columns(table_name)
            }
            for col in table.columns:
                if col.name in existing_cols:
                    continue
                if not col.nullable and col.server_default is None:
                    logging.warning(
                        "auto_migrate: skip NOT NULL column %s.%s (no default)",
                        table_name,
                        col.name,
                    )
                    continue
                col_type = col.type.compile(eng.dialect)
                stmt = (
                    f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}"
                )
                conn.execute(text(stmt))
                logging.info("auto_migrate: added %s.%s", table_name, col.name)
        conn.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
