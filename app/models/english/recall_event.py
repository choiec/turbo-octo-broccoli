from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.english.enums import RecallEventType


class RecallEventBase(SQLModel):
    actor_id: str = Field(index=True)
    occurred_at: datetime = Field(index=True)
    event_type: RecallEventType
    task_item_id: str | None = Field(default=None)
    payload: str | None = Field(default=None)  # JSON
    confidence: float | None = Field(default=None)
    processed: bool = Field(default=False, index=True)


class RecallEvent(RecallEventBase, table=True):
    __tablename__ = "recall_event"
    id: int | None = Field(default=None, primary_key=True)


class RecallEventCreate(RecallEventBase):
    pass


class RecallEventRead(RecallEventBase):
    id: int
