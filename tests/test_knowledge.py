from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

_fake_config = ModuleType("app.core.config")
_fake_settings = MagicMock()
_fake_settings.sqlite_path = ":memory:"
_fake_settings.kuzu_path = "/tmp/test_kuzu"
_fake_settings.entra_tenant_id = "test-tenant"
_fake_settings.entra_client_id = "test-client"
_fake_config.settings = _fake_settings  # type: ignore[attr-defined]
sys.modules["app.core.config"] = _fake_config

sys.modules["app.core.sqlite"] = MagicMock()

from fastapi.testclient import TestClient  # noqa: E402

from app.core.auth import verify_token  # noqa: E402
from app.core.kuzu import get_graph_conn  # noqa: E402
from main import app  # noqa: E402


def fake_verify_token() -> dict[str, object]:
    return {"sub": "test-user"}


app.dependency_overrides[verify_token] = fake_verify_token

client = TestClient(app)


def _make_conn(rows: list[list[object]]) -> MagicMock:
    result = MagicMock()
    result.has_next.side_effect = [True] * len(rows) + [False]
    result.get_next.side_effect = rows
    conn = MagicMock()
    conn.execute.return_value = result
    return conn


def test_list_grammar_by_cefr() -> None:
    conn = _make_conn([["present simple", "CEFR"]])
    app.dependency_overrides[get_graph_conn] = lambda: conn
    response = client.get("/english/inventory/grammar/b1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["guideword"] == "present simple"


def test_list_lexis_by_cefr() -> None:
    conn = _make_conn([["apple", 1]])
    app.dependency_overrides[get_graph_conn] = lambda: conn
    response = client.get("/english/inventory/lexis/b1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["word"] == "apple"
