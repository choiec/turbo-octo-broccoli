"""LexisItem graph: upsert and link to CefrLevel, LexisProfile, LexisSynset."""

from __future__ import annotations

import falkordb


def upsert_lexis_item(
    graph: falkordb.Graph,
    *,
    item_id: str,
    headword: str,
    pos: str | None,
    definition: str,
    synset_id: str | None = None,
    example: str | None = None,
    importance: int | None = None,
    forms: list[str] | None = None,
) -> None:
    """Create or update LexisItem node. Idempotent. Relations via edges."""
    q = (
        "MERGE (i:LexisItem {item_id: $item_id}) "
        "ON CREATE SET i.headword = $headword, i.pos = $pos, "
        "i.definition = $definition, i.synset_id = $synset_id, "
        "i.example = $example, i.importance = $importance, i.forms = $forms "
        "ON MATCH SET i.headword = $headword, i.pos = $pos, "
        "i.definition = $definition, i.synset_id = $synset_id, "
        "i.example = $example, i.importance = $importance, i.forms = $forms"
    )
    graph.query(
        q,
        params={
            "item_id": item_id,
            "headword": headword,
            "pos": pos or "",
            "definition": definition or "",
            "synset_id": synset_id or "",
            "example": example or "",
            "importance": importance,
            "forms": list(forms) if forms is not None else [],
        },
    )


def link_in_synset(
    graph: falkordb.Graph,
    *,
    item_id: str,
    synset_id: str,
) -> None:
    """IN_SYNSET edge from LexisItem to LexisSynset. Creates synset if missing."""
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}) "
        "MERGE (s:LexisSynset {synset_id: $synset_id}) "
        "MERGE (i)-[:IN_SYNSET]->(s)"
    )
    graph.query(q, params={"item_id": item_id, "synset_id": synset_id})


def link_antonym(
    graph: falkordb.Graph,
    *,
    from_id: str,
    to_id: str,
) -> None:
    """ANTONYM edge between two LexisItems. No-op if either node is missing."""
    q = (
        "MATCH (a:LexisItem {item_id: $from_id})"
        ", (b:LexisItem {item_id: $to_id}) "
        "MERGE (a)-[:ANTONYM]->(b)"
    )
    graph.query(q, params={"from_id": from_id, "to_id": to_id})


def link_derivation(
    graph: falkordb.Graph,
    *,
    from_id: str,
    to_id: str,
) -> None:
    """DERIVATION edge between two LexisItems. No-op if either missing."""
    q = (
        "MATCH (a:LexisItem {item_id: $from_id})"
        ", (b:LexisItem {item_id: $to_id}) "
        "MERGE (a)-[:DERIVATION]->(b)"
    )
    graph.query(q, params={"from_id": from_id, "to_id": to_id})


def link_also(
    graph: falkordb.Graph,
    *,
    from_id: str,
    to_id: str,
) -> None:
    """ALSO edge between two LexisItems. No-op if either node is missing."""
    q = (
        "MATCH (a:LexisItem {item_id: $from_id})"
        ", (b:LexisItem {item_id: $to_id}) "
        "MERGE (a)-[:ALSO]->(b)"
    )
    graph.query(q, params={"from_id": from_id, "to_id": to_id})


def link_similar(
    graph: falkordb.Graph,
    *,
    from_id: str,
    to_id: str,
) -> None:
    """SIMILAR edge between two LexisItems. No-op if either node is missing."""
    q = (
        "MATCH (a:LexisItem {item_id: $from_id})"
        ", (b:LexisItem {item_id: $to_id}) "
        "MERGE (a)-[:SIMILAR]->(b)"
    )
    graph.query(q, params={"from_id": from_id, "to_id": to_id})


def link_synset_hypernym(
    graph: falkordb.Graph,
    *,
    from_synset_id: str,
    to_synset_id: str,
) -> None:
    """HYPERNYM edge between two LexisSynsets. Nodes created if missing."""
    q = (
        "MERGE (from_s:LexisSynset {synset_id: $from_synset_id}) "
        "MERGE (to_s:LexisSynset {synset_id: $to_synset_id}) "
        "MERGE (from_s)-[:HYPERNYM]->(to_s)"
    )
    graph.query(
        q,
        params={"from_synset_id": from_synset_id, "to_synset_id": to_synset_id},
    )


def link_cefr(
    graph: falkordb.Graph,
    *,
    item_id: str,
    cefr: str,
) -> None:
    """Link LexisItem to CefrLevel via LEXIS_LEVEL. Idempotent."""
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}) "
        "MERGE (c:CefrLevel {code: $cefr}) "
        "MERGE (i)-[:LEXIS_LEVEL]->(c)"
    )
    graph.query(q, params={"item_id": item_id, "cefr": cefr.lower()})


def link_profile(
    graph: falkordb.Graph,
    *,
    item_id: str,
    headword: str,
) -> None:
    """Link LexisItem to LexisProfile (HAS_PROFILE). No-op if absent."""
    q = (
        "MATCH (i:LexisItem {item_id: $item_id}), "
        "(l:LexisProfile {headword: $headword}) "
        "MERGE (i)-[:HAS_PROFILE]->(l)"
    )
    graph.query(q, params={"item_id": item_id, "headword": headword})
