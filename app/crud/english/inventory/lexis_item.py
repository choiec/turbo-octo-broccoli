"""LexisItem graph: list and re-export write ops."""

from __future__ import annotations

import json

import falkordb

from app.crud.english.inventory.lexis_item_write import (  # noqa: F401
    link_also,
    link_antonym,
    link_cefr,
    link_derivation,
    link_in_synset,
    link_profile,
    link_similar,
    link_synset_hypernym,
    upsert_lexis_item,
)
from app.schemas.english.inventory.lexis_item import (
    LexisItemSchema,
    LexisItemWithProfile,
)

_LIST_BY_ITEM_IDS_QUERY = (
    "MATCH (i:LexisItem) WHERE i.item_id IN $item_ids "
    "OPTIONAL MATCH (i)-[:LEXIS_LEVEL]->(c:CefrLevel) "
    "OPTIONAL MATCH (i)-[:IN_SYNSET]->(s:LexisSynset) "
    "OPTIONAL MATCH (s)<-[:IN_SYNSET]-(sib:LexisItem) WHERE sib <> i "
    "OPTIONAL MATCH (i)-[:ANTONYM]->(ant:LexisItem) "
    "OPTIONAL MATCH (i)-[:DERIVATION]->(der:LexisItem) "
    "OPTIONAL MATCH (i)-[:ALSO]->(also_i:LexisItem) "
    "OPTIONAL MATCH (i)-[:SIMILAR]->(sim:LexisItem) "
    "OPTIONAL MATCH (s)-[:HYPERNYM]->(hype:LexisSynset) "
    "OPTIONAL MATCH (s)<-[:HYPERNYM]-(hypo:LexisSynset) "
    "RETURN i.item_id, i.headword, i.pos, i.definition, i.synset_id, "
    "i.example, i.importance, i.forms, c.code, "
    "collect(DISTINCT sib.item_id), collect(DISTINCT ant.item_id), "
    "collect(DISTINCT der.item_id), collect(DISTINCT also_i.item_id), "
    "collect(DISTINCT sim.item_id), collect(DISTINCT hype.synset_id), "
    "collect(DISTINCT hypo.synset_id)"
)

_LIST_BY_ITEM_IDS_WITH_PROFILE_QUERY = (
    "MATCH (i:LexisItem) WHERE i.item_id IN $item_ids "
    "OPTIONAL MATCH (i)-[:LEXIS_LEVEL]->(c:CefrLevel) "
    "OPTIONAL MATCH (i)-[:HAS_PROFILE]->(l:LexisProfile) "
    "OPTIONAL MATCH (i)-[:IN_SYNSET]->(s:LexisSynset) "
    "OPTIONAL MATCH (s)<-[:IN_SYNSET]-(sib:LexisItem) WHERE sib <> i "
    "OPTIONAL MATCH (i)-[:ANTONYM]->(ant:LexisItem) "
    "OPTIONAL MATCH (i)-[:DERIVATION]->(der:LexisItem) "
    "OPTIONAL MATCH (i)-[:ALSO]->(also_i:LexisItem) "
    "OPTIONAL MATCH (i)-[:SIMILAR]->(sim:LexisItem) "
    "OPTIONAL MATCH (s)-[:HYPERNYM]->(hype:LexisSynset) "
    "OPTIONAL MATCH (s)<-[:HYPERNYM]-(hypo:LexisSynset) "
    "RETURN i.item_id, i.headword, i.pos, i.definition, i.synset_id, "
    "i.example, i.importance, i.forms, c.code, l.total_freq, l.total_nb_doc, "
    "collect(DISTINCT sib.item_id), collect(DISTINCT ant.item_id), "
    "collect(DISTINCT der.item_id), collect(DISTINCT also_i.item_id), "
    "collect(DISTINCT sim.item_id), collect(DISTINCT hype.synset_id), "
    "collect(DISTINCT hypo.synset_id)"
)


def _norm_collect(v: object) -> list[str]:
    """Coerce collect() result to list of non-null strings."""
    if isinstance(v, list):
        return [x for x in v if x is not None and isinstance(x, str)]
    return []


def _norm_forms(v: object) -> list[str]:
    """Coerce forms property (list or JSON string) to list of strings."""
    if isinstance(v, list):
        return [x for x in v if isinstance(x, str)]
    if isinstance(v, str) and v:
        try:
            parsed = json.loads(v)
            return (
                [x for x in parsed if isinstance(x, str)]
                if isinstance(parsed, list)
                else []
            )
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def list_by_item_ids(
    graph: falkordb.Graph, item_ids: list[str]
) -> list[LexisItemSchema]:
    """Return LexisItems for the given item_ids with optional CEFR."""
    if not item_ids:
        return []
    result = graph.query(_LIST_BY_ITEM_IDS_QUERY, params={"item_ids": item_ids})
    return [
        LexisItemSchema(
            item_id=row[0],
            headword=row[1] or "",
            pos=row[2] or None,
            definition=row[3] or "",
            synset_id=row[4] or None,
            example=row[5] or None,
            importance=(int(row[6]) if row[6] is not None else None),
            forms=_norm_forms(row[7]),
            cefr=(row[8].lower() if row[8] else None),
            synonyms=_norm_collect(row[9]),
            antonyms=_norm_collect(row[10]),
            derivations=_norm_collect(row[11]),
            also_ids=_norm_collect(row[12]),
            similar_ids=_norm_collect(row[13]),
            hypernym_ids=_norm_collect(row[14]),
            hyponym_ids=_norm_collect(row[15]),
        )
        for row in result.result_set
    ]


def list_by_item_ids_with_profile(
    graph: falkordb.Graph, item_ids: list[str]
) -> list[LexisItemWithProfile]:
    """Return LexisItems for item_ids with optional CEFR and LexisProfile."""
    if not item_ids:
        return []
    result = graph.query(
        _LIST_BY_ITEM_IDS_WITH_PROFILE_QUERY, params={"item_ids": item_ids}
    )
    return [
        LexisItemWithProfile(
            item_id=row[0],
            headword=row[1] or "",
            pos=row[2] or None,
            definition=row[3] or "",
            synset_id=row[4] or None,
            example=row[5] or None,
            importance=(int(row[6]) if row[6] is not None else None),
            forms=_norm_forms(row[7]),
            cefr=(row[8].lower() if row[8] else None),
            total_freq=(float(row[9]) if row[9] is not None else None),
            total_nb_doc=(int(row[10]) if row[10] is not None else None),
            synonyms=_norm_collect(row[11]),
            antonyms=_norm_collect(row[12]),
            derivations=_norm_collect(row[13]),
            also_ids=_norm_collect(row[14]),
            similar_ids=_norm_collect(row[15]),
            hypernym_ids=_norm_collect(row[16]),
            hyponym_ids=_norm_collect(row[17]),
        )
        for row in result.result_set
    ]
