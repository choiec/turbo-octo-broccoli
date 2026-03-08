"""CefrLevel node helpers for FalkorDB inventory graph."""

from __future__ import annotations

import falkordb

CEFR_CODES = ("A1", "A2", "B1", "B2", "C1", "C2")


def ensure_cefr_levels(graph: falkordb.Graph) -> None:
    """Ensure CefrLevel nodes exist for A1..C2. Idempotent."""
    for code in CEFR_CODES:
        graph.query(
            "MERGE (c:CefrLevel {code: $code})",
            params={"code": code},
        )
