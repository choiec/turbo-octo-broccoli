from __future__ import annotations

from sqlmodel import Field, SQLModel


class LexisCorpusFreq(SQLModel, table=True):
    """Per-corpus, per-CEFR frequency for a lexical item.

    Tabular lookup data; not part of the FalkorDB knowledge graph.
    Headword corresponds to LexisProfile node in FalkorDB.
    """

    __tablename__ = "lexis_corpus_freq"
    headword: str = Field(primary_key=True)
    corpus_name: str = Field(primary_key=True)
    cefr_level: str = Field(primary_key=True)
    freq: float
