"""KICE exam text graph: Source, Testlet, ExamQuestion nodes and edges."""

from __future__ import annotations

import falkordb


def upsert_source(
    graph: falkordb.Graph,
    *,
    source_id: str,
    year: int,
    month: int,
    exam_type: str,
    academic_year: int,
    issuer: str = "KICE",
) -> None:
    """Create or update a Source node.
    Call before upsert_testlet/upsert_question.
    """
    q = (
        "MERGE (s:Source {source_id: $source_id}) "
        "ON CREATE SET s.year = $year, s.month = $month, "
        "s.exam_type = $exam_type, s.academic_year = $academic_year, "
        "s.issuer = $issuer"
    )
    graph.query(
        q,
        params={
            "source_id": source_id,
            "year": year,
            "month": month,
            "exam_type": exam_type,
            "academic_year": academic_year,
            "issuer": issuer,
        },
    )


def upsert_testlet(
    graph: falkordb.Graph,
    *,
    testlet_id: str,
    source_id: str,
    question_group: str,
    text: str,
    footnotes: str = "",
) -> None:
    """Create/update Testlet and link to Source.
    Call upsert_source first.
    """
    q = (
        "MERGE (t:Testlet {testlet_id: $testlet_id}) "
        "ON CREATE SET t.source_id = $source_id, "
        "t.question_group = $question_group, t.text = $text, "
        "t.footnotes = $footnotes "
        "WITH t MERGE (s:Source {source_id: $source_id}) "
        "MERGE (t)-[:IN_SOURCE]->(s)"
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


def upsert_question(
    graph: falkordb.Graph,
    *,
    question_id: str,
    source_id: str,
    number: int,
    section: str,
    question_type: str,
    stem: str,
    options: str,
    answer: int,
    score: int,
    testlet_id: str | None = None,
) -> None:
    """Create/update ExamQuestion, link to Source; optionally to Testlet."""
    q = (
        "MERGE (q:ExamQuestion {question_id: $question_id}) "
        "ON CREATE SET q.source_id = $source_id, q.number = $number, "
        "q.section = $section, q.question_type = $question_type, "
        "q.stem = $stem, q.options = $options, "
        "q.answer = $answer, q.score = $score "
        "WITH q MERGE (s:Source {source_id: $source_id}) "
        "MERGE (q)-[:IN_SOURCE]->(s)"
    )
    params: dict = {
        "question_id": question_id,
        "source_id": source_id,
        "number": number,
        "section": section,
        "question_type": question_type,
        "stem": stem,
        "options": options,
        "answer": answer,
        "score": score,
    }
    graph.query(q, params=params)
    if testlet_id:
        q2 = (
            "MATCH (q:ExamQuestion {question_id: $question_id}) "
            "MATCH (t:Testlet {testlet_id: $testlet_id}) "
            "MERGE (q)-[:QUESTION_OF]->(t)"
        )
        graph.query(
            q2, params={"question_id": question_id, "testlet_id": testlet_id}
        )
