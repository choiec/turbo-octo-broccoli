"""Response schemas for LexisItem (inventory)."""

from __future__ import annotations

from pydantic import BaseModel


class LexisItemSchema(BaseModel):
    """Response schema for a single lexis set item."""

    item_id: str
    headword: str
    pos: str | None
    definition: str
    synset_id: str | None = None
    example: str | None = None
    cefr: str | None = None
    importance: int | None = None
    forms: list[str] = []
    synonyms: list[str] = []
    antonyms: list[str] = []
    derivations: list[str] = []
    hypernym_ids: list[str] = []
    hyponym_ids: list[str] = []
    similar_ids: list[str] = []
    also_ids: list[str] = []


class LexisItemWithProfile(LexisItemSchema):
    """LexisItem with optional LexisProfile (total_freq, total_nb_doc)."""

    total_freq: float | None = None
    total_nb_doc: int | None = None
