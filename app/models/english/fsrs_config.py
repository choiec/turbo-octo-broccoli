from __future__ import annotations

from sqlmodel import Field, SQLModel


class FsrsConfigBase(SQLModel):
    learner_id: str = Field(unique=True, index=True)
    w_vector: str  # JSON array of 19 floats (FSRS-5 default)


class FsrsConfig(FsrsConfigBase, table=True):
    __tablename__ = "fsrs_config"
    id: int | None = Field(default=None, primary_key=True)


class FsrsConfigCreate(FsrsConfigBase):
    pass


class FsrsConfigRead(FsrsConfigBase):
    id: int
