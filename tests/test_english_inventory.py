from __future__ import annotations

import sys
from collections.abc import Generator
from types import ModuleType
from unittest.mock import MagicMock, patch

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
from app.core.sqlite import get_session  # noqa: E402
from main import app  # noqa: E402


def fake_verify_token() -> dict[str, object]:
    return {"sub": "test-user"}


def fake_get_session() -> Generator[MagicMock, None, None]:
    yield MagicMock()


app.dependency_overrides[verify_token] = fake_verify_token
app.dependency_overrides[get_session] = fake_get_session

client = TestClient(app)

_LEXIS_BASE = "/english/records/lexis/review/schedule"


def _mock_graph_conn(
    rows: list[list[object]],
) -> Generator[MagicMock, None, None]:
    graph = MagicMock()
    graph.query.return_value = MagicMock(result_set=rows)
    yield graph


def test_list_grammar_by_cefr() -> None:
    app.dependency_overrides[get_graph_conn] = lambda: next(
        _mock_graph_conn(
            [
                [
                    "present simple",
                    "VERBS",
                    "tense",
                    "FORM",
                    "can use",
                    "He works.",
                    "",
                    "b1",
                ]
            ]
        )
    )
    response = client.get("/english/inventory/grammar/b1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["guideword"] == "present simple"
    assert data[0]["can_do"] == "can use"
    assert data[0]["example"] == "He works."
    assert data[0]["cefr_level"] == "b1"


def test_list_lexis_by_cefr() -> None:
    app.dependency_overrides[get_graph_conn] = lambda: next(
        _mock_graph_conn([["apple", "NN", 1.0, 5, 0.5, 2]])
    )
    response = client.get("/english/inventory/lexis/b1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["headword"] == "apple"


def test_task_is_lexis_tagged_and_link_lexis() -> None:
    from app.crud.english.inventory import task as task_crud

    graph = MagicMock()
    graph.query.return_value = MagicMock(result_set=[[1]])
    assert task_crud.is_lexis_tagged(graph, "tid") is True
    graph.query.assert_called()
    call_args = graph.query.call_args
    assert "CONTAINS_LEXIS" in call_args[0][0]
    assert call_args[1]["params"]["task_id"] == "tid"

    graph.reset_mock()
    graph.query.return_value = MagicMock(result_set=[])
    task_crud.link_lexis(graph, task_id="tid", headword="apple")
    graph.query.assert_called_once()
    call_args = graph.query.call_args
    assert "CONTAINS_LEXIS" in call_args[0][0]
    assert call_args[1]["params"]["task_id"] == "tid"
    assert call_args[1]["params"]["headword"] == "apple"


def test_task_set_task_cefr() -> None:
    from app.crud.english.inventory import task as task_crud

    graph = MagicMock()
    task_crud.set_task_cefr(graph, "tid", lexis_cefr="b1", grammar_cefr="b2")
    graph.query.assert_called_once()
    call_args = graph.query.call_args
    assert "lexis_cefr" in call_args[0][0] and "grammar_cefr" in call_args[0][0]
    assert call_args[1]["params"]["lexis_cefr"] == "b1"
    assert call_args[1]["params"]["grammar_cefr"] == "b2"


def test_task_list_by_cefr() -> None:
    from app.crud.english.inventory import task as task_crud

    graph = MagicMock()
    graph.query.return_value = MagicMock(
        result_set=[
            ["tid1", "src1", "18", "b1", "b2"],
            ["tid2", "src2", "41", None, "b1"],
        ]
    )
    tasks = task_crud.list_by_cefr(graph, "b1")
    graph.query.assert_called_once()
    call_args = graph.query.call_args
    assert "lexis_cefr" in call_args[0][0] and "grammar_cefr" in call_args[0][0]
    assert call_args[1]["params"]["cefr"] == "b1"
    assert len(tasks) == 2
    assert tasks[0].task_id == "tid1"
    assert tasks[0].lexis_cefr == "b1"
    assert tasks[0].grammar_cefr == "b2"
    assert tasks[1].task_id == "tid2"
    assert tasks[1].lexis_cefr is None
    assert tasks[1].grammar_cefr == "b1"


def test_tag_lexis_tasks_empty_list_returns_zero() -> None:
    from app.scripts.tag_lexis import tag_tasks

    graph = MagicMock()
    assert tag_tasks(graph, []) == 0
    graph.query.assert_not_called()


def test_tag_lexis_tasks_skips_without_raising() -> None:
    """tag_tasks with non-empty list never raises (spacy missing => 0)."""
    from app.scripts.tag_lexis import tag_tasks

    graph = MagicMock()
    graph.query.return_value = MagicMock(result_set=[])
    n = tag_tasks(graph, [("t1", "hello world")])
    assert isinstance(n, int)
    assert n >= 0


# ── lexis-review-schedule (records) ───────────────────────────────────────────


def test_lexis_review_schedule_post_ok() -> None:
    from datetime import datetime
    from types import SimpleNamespace

    payload = {
        "learner_id": "u1",
        "item_id": "lex-item-1",
        "attempt_quality": 3,
    }
    mock_row = SimpleNamespace(
        id=1,
        learner_id="u1",
        item_id="lex-item-1",
        fsrs_state=None,
        stability=1.0,
        difficulty=1.0,
        due_date=datetime(2026, 3, 11),
        retrievability=0.9,
    )
    _p = (
        "app.routers.english.records.lexis_review_schedule.crud"
        ".upsert_lexis_review_schedule"
    )
    with patch(_p) as m:
        m.return_value = mock_row
        resp = client.post(_LEXIS_BASE, json=payload)
    assert resp.status_code == 200
    assert resp.json()["item_id"] == "lex-item-1"


def test_lexis_review_schedule_get_due_ok() -> None:
    _p = (
        "app.routers.english.records.lexis_review_schedule.crud"
        ".list_due_lexis_items"
    )
    with patch(_p) as m:
        m.return_value = []
        resp = client.get(f"{_LEXIS_BASE}/due/u1")
    assert resp.status_code == 200
    assert resp.json() == []


def test_lexis_review_schedule_get_list_ok() -> None:
    _p = (
        "app.routers.english.records.lexis_review_schedule.crud"
        ".list_lexis_review_schedule"
    )
    with patch(_p) as m:
        m.return_value = []
        resp = client.get(f"{_LEXIS_BASE}/u1")
    assert resp.status_code == 200
    assert resp.json() == []
