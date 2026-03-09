"""Testlet graph: Testlet (passage). Source in SQLite. Items are separate."""

from __future__ import annotations

import falkordb


def upsert_testlet(
    graph: falkordb.Graph,
    *,
    testlet_id: str,
    source_id: str,
    question_group: str,
    text: str,
    footnotes: str = "",
) -> None:
    """Create or update Testlet node (passage only).
    source_id references Source in SQLite; caller must ensure it exists.
    Items are stored as separate Item nodes linked via HAS_ITEM.
    """
    q = (
        "MERGE (t:Testlet {testlet_id: $testlet_id}) "
        "ON CREATE SET t.source_id = $source_id, "
        "t.question_group = $question_group, t.text = $text, "
        "t.footnotes = $footnotes "
        "ON MATCH SET t.text = $text, t.footnotes = $footnotes"
    )
    graph.query(
        q,
        params={
            "testlet_id": testlet_id,
            "source_id": source_id,
            "question_group": question_group,
            "text": text,
            "footnotes": footnotes,
        },
    )


def fetch_all(graph: falkordb.Graph) -> list[tuple[str, str]]:
    """Return (testlet_id, text) for all Testlets with non-empty text."""
    q = (
        "MATCH (t:Testlet) WHERE t.text IS NOT NULL AND t.text <> '' "
        "RETURN t.testlet_id, t.text"
    )
    result = graph.query(q)
    return [(row[0], row[1]) for row in result.result_set]


def is_grammar_tagged(graph: falkordb.Graph, testlet_id: str) -> bool:
    """True if this Testlet has at least one CONTAINS_GRAMMAR edge."""
    q = (
        "MATCH (t:Testlet {testlet_id: $testlet_id})-[:CONTAINS_GRAMMAR]->() "
        "RETURN 1 LIMIT 1"
    )
    result = graph.query(q, params={"testlet_id": testlet_id})
    return len(result.result_set) > 0


def link_grammar(
    graph: falkordb.Graph,
    *,
    testlet_id: str,
    guideword: str,
) -> None:
    """Create Testlet -[:CONTAINS_GRAMMAR]-> GrammarProfile. No-op if missing."""
    q = (
        "MATCH (t:Testlet {testlet_id: $testlet_id}) "
        "MATCH (g:GrammarProfile {guideword: $guideword}) "
        "MERGE (t)-[:CONTAINS_GRAMMAR]->(g)"
    )
    graph.query(q, params={"testlet_id": testlet_id, "guideword": guideword})
