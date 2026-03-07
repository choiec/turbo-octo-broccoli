from __future__ import annotations

from sqlmodel import Field, SQLModel

from app.models.english.enums import EnglishSystem


class AcquisitionBase(SQLModel):
    learner_id: str = Field(index=True)
    domain: EnglishSystem
    item: str
    stage: str | None = Field(default=None)
    frequency: int | None = Field(default=None)


class Acquisition(AcquisitionBase, table=True):
    __tablename__ = "english_acquisition"
    id: int | None = Field(default=None, primary_key=True)


class AcquisitionCreate(AcquisitionBase):
    pass


class AcquisitionRead(AcquisitionBase):
    id: int


class AcquisitionUpdate(SQLModel):
    stage: str | None = None
    frequency: int | None = None
