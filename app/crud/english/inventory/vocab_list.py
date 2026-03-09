"""VocabList graph: vocabulary lists (단어장) containing LexisItems."""

from __future__ import annotations

import falkordb
from pydantic import BaseModel


class VocabListMeta(BaseModel):
    """Metadata for a single vocab list."""

    list_id: str
    name: str
    book: str
    day_num: int


_LIST_ALL_QUERY = (
    "MATCH (v:VocabList) RETURN v.list_id, v.name, v.book, v.day_num"
)


def upsert_vocab_list(
    graph: falkordb.Graph,
    *,
    list_id: str,
    name: str,
    book: str,
    day_num: int,
) -> None:
    """Create or update VocabList node. Idempotent."""
    q = (
        "MERGE (v:VocabList {list_id: $list_id}) "
        "ON CREATE SET v.name = $name, v.book = $book, v.day_num = $day_num "
        "ON MATCH SET v.name = $name, v.book = $book, v.day_num = $day_num"
    )
    graph.query(
        q,
        params={
            "list_id": list_id,
            "name": name,
            "book": book,
            "day_num": day_num,
        },
    )


def link_item(
    graph: falkordb.Graph,
    *,
    list_id: str,
    item_id: str,
) -> None:
    """Link VocabList to LexisItem via CONTAINS. Idempotent."""
    q = (
        "MATCH (v:VocabList {list_id: $list_id}), "
        "(i:LexisItem {item_id: $item_id}) MERGE (v)-[:CONTAINS]->(i)"
    )
    graph.query(q, params={"list_id": list_id, "item_id": item_id})


def list_all(graph: falkordb.Graph) -> list[VocabListMeta]:
    """Return all VocabList nodes."""
    result = graph.query(_LIST_ALL_QUERY)
    return [
        VocabListMeta(
            list_id=row[0],
            name=row[1] or "",
            book=row[2] or "",
            day_num=int(row[3]) if row[3] is not None else 0,
        )
        for row in result.result_set
    ]
