"""add_grammar_set_lexis_set

Revision ID: e5f6a7b8c9d0
Revises: a1b2c3d4e5f6
Create Date: 2026-03-10 16:00:00.000000

Create grammar_set, grammar_set_item, lexis_set, lexis_set_item tables (SQLite).

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlmodel.sql import sqltypes

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "grammar_set",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("set_id", sqltypes.AutoString(), nullable=False),
        sa.Column("source", sqltypes.AutoString(), nullable=False),
        sa.Column("unit_num", sa.Integer(), nullable=False),
        sa.Column("title", sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_grammar_set_set_id"), "grammar_set", ["set_id"], unique=True
    )

    op.create_table(
        "grammar_set_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("set_id", sqltypes.AutoString(), nullable=False),
        sa.Column("guideword", sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["set_id"], ["grammar_set.set_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "set_id", "guideword", name="uq_grammar_set_item_set_id_guideword"
        ),
    )
    op.create_index(
        op.f("ix_grammar_set_item_guideword"),
        "grammar_set_item",
        ["guideword"],
        unique=False,
    )
    op.create_index(
        op.f("ix_grammar_set_item_set_id"),
        "grammar_set_item",
        ["set_id"],
        unique=False,
    )

    op.create_table(
        "lexis_set",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("set_id", sqltypes.AutoString(), nullable=False),
        sa.Column("source", sqltypes.AutoString(), nullable=False),
        sa.Column("unit_num", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_lexis_set_set_id"), "lexis_set", ["set_id"], unique=True
    )

    op.create_table(
        "lexis_set_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("set_id", sqltypes.AutoString(), nullable=False),
        sa.Column("item_id", sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["set_id"], ["lexis_set.set_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "set_id", "item_id", name="uq_lexis_set_item_set_id_item_id"
        ),
    )
    op.create_index(
        op.f("ix_lexis_set_item_item_id"),
        "lexis_set_item",
        ["item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lexis_set_item_set_id"),
        "lexis_set_item",
        ["set_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_lexis_set_item_set_id"), table_name="lexis_set_item")
    op.drop_index(
        op.f("ix_lexis_set_item_item_id"), table_name="lexis_set_item"
    )
    op.drop_table("lexis_set_item")
    op.drop_index(op.f("ix_lexis_set_set_id"), table_name="lexis_set")
    op.drop_table("lexis_set")
    op.drop_index(
        op.f("ix_grammar_set_item_set_id"), table_name="grammar_set_item"
    )
    op.drop_index(
        op.f("ix_grammar_set_item_guideword"), table_name="grammar_set_item"
    )
    op.drop_table("grammar_set_item")
    op.drop_index(op.f("ix_grammar_set_set_id"), table_name="grammar_set")
    op.drop_table("grammar_set")
