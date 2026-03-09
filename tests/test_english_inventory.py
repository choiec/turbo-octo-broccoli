from __future__ import annotations

import sys
from collections.abc import Generator
from types import ModuleType
from unittest.mock import MagicMock

_fake_config = ModuleType("app.core.config")
_fake_settings = MagicMock()
_fake_settings.sqlite_path = ":memory:"
_fake_settings.falkordb_host = "localhost"
_fake_settings.falkordb_port = 56379
_fake_settings.falkordb_graph = "knowledge_graph"
_fake_settings.entra_tenant_id = "test-tenant"
_fake_settings.entra_client_id = "test-client"
_fake_config.settings = _fake_settings  # type: ignore[attr-defined]
sys.modules["app.core.config"] = _fake_config

sys.modules["app.core.sqlite"] = MagicMock()

from fastapi.testclient import TestClient  # noqa: E402

from app.core.auth import verify_token  # noqa: E402
from app.core.falkordb import get_graph_conn  # noqa: E402
from main import app  # noqa: E402


def fake_verify_token() -> dict[str, object]:
    return {"sub": "test-user"}


app.dependency_overrides[verify_token] = fake_verify_token

client = TestClient(app)


def _mock_graph_conn(
    rows: list[list[object]],
) -> Generator[MagicMock, None, None]:
    graph = MagicMock()
    graph.query.return_value = MagicMock(result_set=rows)
    yield graph


def test_list_grammar_by_cefr() -> None:
    app.dependency_overrides[get_graph_conn] = lambda: next(
        _mock_graph_conn(
            [["present simple", "VERBS", "tense", "FORM", "can use", "He works.", ""]]
        )
    )
    response = client.get("/english/inventory/grammar/b1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["guideword"] == "present simple"
    assert data[0]["can_do"] == "can use"
    assert data[0]["example"] == "He works."


def test_list_lexis_by_cefr() -> None:
    app.dependency_overrides[get_graph_conn] = lambda: next(
        _mock_graph_conn([["apple", "NN", 1.0, 5, 0.5, 2]])
    )
    response = client.get("/english/inventory/lexis/b1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["headword"] == "apple"
