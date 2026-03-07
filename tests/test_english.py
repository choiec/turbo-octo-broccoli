from __future__ import annotations

import sys
from collections.abc import Generator
from datetime import datetime
from types import ModuleType
from unittest.mock import MagicMock, patch

_fake_config = ModuleType("app.core.config")
_fake_settings = MagicMock()
_fake_settings.sqlite_path = ":memory:"
_fake_settings.kuzu_path = "/tmp/test_kuzu"
_fake_settings.openai_api_key = ""
_fake_settings.entra_tenant_id = "test-tenant"
_fake_settings.entra_client_id = "test-client"
_fake_config.settings = _fake_settings  # type: ignore[attr-defined]
_fake_config.Settings = MagicMock(  # type: ignore[attr-defined]
    return_value=_fake_settings
)
sys.modules["app.core.config"] = _fake_config

_fake_kuzu = ModuleType("app.core.kuzu")
_fake_kuzu.db = MagicMock()  # type: ignore[attr-defined]
_fake_kuzu.get_graph_conn = MagicMock()  # type: ignore[attr-defined]
_fake_kuzu.init_graph_schema = MagicMock()  # type: ignore[attr-defined]
sys.modules["app.core.kuzu"] = _fake_kuzu

from fastapi.testclient import TestClient  # noqa: E402

from app.core.auth import verify_token  # noqa: E402
from app.core.sqlite import get_session  # noqa: E402
from app.models.english.acquisition import AcquisitionRead  # noqa: E402
from app.models.english.learner_proficiency import (  # noqa: E402
    LearnerProficiencyRead,
)
from app.models.english.practice import PracticeRead  # noqa: E402
from app.models.english.task_outcome import TaskOutcomeRead  # noqa: E402
from app.models.english.writing_assessment import (  # noqa: E402
    WritingAssessmentRead,
)
from main import app  # noqa: E402


def fake_verify_token() -> dict[str, object]:
    return {"sub": "test-user"}


def fake_get_session() -> Generator[MagicMock, None, None]:
    yield MagicMock()


app.dependency_overrides[verify_token] = fake_verify_token
app.dependency_overrides[get_session] = fake_get_session

client = TestClient(app)

_BASE = "/english/records"
_NOW = datetime.now().isoformat()


# ── practice ──────────────────────────────────────────────────────────────────


def test_create_practice_missing_fields() -> None:
    resp = client.post(f"{_BASE}/practice", json={})
    assert resp.status_code == 422


def test_create_practice_ok() -> None:
    payload = {
        "learner_id": "u1",
        "domain": "grammar",
        "item": "present simple",
    }
    ret = PracticeRead.model_validate({"id": 1, **payload})
    _p = "app.routers.english.records.practice.crud.create_practice"
    with patch(_p) as m:
        m.return_value = ret
        resp = client.post(f"{_BASE}/practice", json=payload)
    assert resp.status_code == 200


def test_list_practice_ok() -> None:
    with patch("app.routers.english.records.practice.crud.list_practice") as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/practice/u1")
    assert resp.status_code == 200
    assert resp.json() == []


# ── acquisition ───────────────────────────────────────────────────────────────


def test_create_acquisition_missing_fields() -> None:
    resp = client.post(f"{_BASE}/acquisition", json={})
    assert resp.status_code == 422


def test_create_acquisition_ok() -> None:
    payload = {
        "learner_id": "u1",
        "domain": "lexis",
        "item": "ubiquitous",
    }
    ret = AcquisitionRead.model_validate({"id": 1, **payload})
    _p = "app.routers.english.records.acquisition.crud.create_acquisition"
    with patch(_p) as m:
        m.return_value = ret
        resp = client.post(f"{_BASE}/acquisition", json=payload)
    assert resp.status_code == 200


def test_list_acquisition_ok() -> None:
    _p = "app.routers.english.records.acquisition.crud.list_acquisition"
    with patch(_p) as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/acquisition/u1")
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_acquisition_not_found() -> None:
    _p = "app.routers.english.records.acquisition.crud.update_acquisition"
    with patch(_p) as m:
        m.side_effect = ValueError("not found")
        resp = client.put(f"{_BASE}/acquisition/999", json={})
    assert resp.status_code == 404


# ── learner_proficiency ───────────────────────────────────────────────────────


def test_create_learner_proficiency_missing_fields() -> None:
    resp = client.post(f"{_BASE}/learner-proficiency", json={})
    assert resp.status_code == 422


def test_create_learner_proficiency_ok() -> None:
    payload = {
        "learner_id": "u1",
        "skill": "reading",
        "cefr_level": "B2",
    }
    ret = LearnerProficiencyRead.model_validate({"id": 1, **payload})
    with patch(
        "app.routers.english.records.learner_proficiency.crud"
        ".create_learner_proficiency"
    ) as m:
        m.return_value = ret
        resp = client.post(f"{_BASE}/learner-proficiency", json=payload)
    assert resp.status_code == 200


def test_list_learner_proficiency_ok() -> None:
    with patch(
        "app.routers.english.records.learner_proficiency.crud"
        ".list_learner_proficiency"
    ) as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/learner-proficiency/u1")
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_learner_proficiency_not_found() -> None:
    with patch(
        "app.routers.english.records.learner_proficiency.crud"
        ".update_learner_proficiency"
    ) as m:
        m.side_effect = ValueError("not found")
        resp = client.put(f"{_BASE}/learner-proficiency/999", json={})
    assert resp.status_code == 404


# ── needs_analysis ────────────────────────────────────────────────────────────


def test_list_needs_analysis_ok() -> None:
    with patch(
        "app.routers.english.records.needs_analysis.crud.list_needs_analysis"
    ) as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/needs-analysis")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_needs_analysis_with_filter() -> None:
    with patch(
        "app.routers.english.records.needs_analysis.crud.list_needs_analysis"
    ) as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/needs-analysis?cefr_level=B1")
    assert resp.status_code == 200


# ── task_outcome ──────────────────────────────────────────────────────────────


def test_create_task_outcome_missing_fields() -> None:
    resp = client.post(f"{_BASE}/task-outcome", json={})
    assert resp.status_code == 422


def test_create_task_outcome_ok() -> None:
    payload = {"learner_id": "u1", "session_at": _NOW}
    ret = TaskOutcomeRead.model_validate({"id": 1, **payload})
    with patch(
        "app.routers.english.records.task_outcome.crud.create_task_outcome"
    ) as m:
        m.return_value = ret
        resp = client.post(f"{_BASE}/task-outcome", json=payload)
    assert resp.status_code == 200


def test_list_task_outcomes_ok() -> None:
    _p = "app.routers.english.records.task_outcome.crud.list_task_outcomes"
    with patch(_p) as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/task-outcome/u1")
    assert resp.status_code == 200
    assert resp.json() == []


# ── writing_assessment ────────────────────────────────────────────────────────


def test_create_writing_assessment_missing_fields() -> None:
    resp = client.post(f"{_BASE}/writing-assessment", json={})
    assert resp.status_code == 422


def test_create_writing_assessment_ok() -> None:
    payload = {
        "learner_id": "u1",
        "session_at": _NOW,
        "content": 8,
        "grammar": 7,
        "lexis": 8,
        "organization": 7,
        "english_total": 30,
    }
    ret = WritingAssessmentRead.model_validate({"id": 1, **payload})
    with patch(
        "app.routers.english.records.writing_assessment.crud"
        ".create_writing_assessment"
    ) as m:
        m.return_value = ret
        resp = client.post(f"{_BASE}/writing-assessment", json=payload)
    assert resp.status_code == 200


def test_list_writing_assessments_ok() -> None:
    with patch(
        "app.routers.english.records.writing_assessment.crud"
        ".list_writing_assessments"
    ) as m:
        m.return_value = []
        resp = client.get(f"{_BASE}/writing-assessment/u1")
    assert resp.status_code == 200
    assert resp.json() == []
