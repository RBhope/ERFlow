from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from django.test import Client

from erflow import api
from erflow.modules.data_store import RecordStore
from erflow.modules.recommendation import RecommendationProvider


class FakeRecordStore(RecordStore):
    def __init__(self) -> None:
        self.records: dict[str, list[dict[str, Any]]] = {}

    def save(self, record_type: str, record: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(record)
        self.records.setdefault(record_type, []).append(stored)
        return stored

    def get(self, record_type: str, record_id: str) -> Mapping[str, Any] | None:
        for record in self.records.get(record_type, []):
            if record.get("id") == record_id:
                return record
        return None

    def list(self, record_type: str) -> Sequence[Mapping[str, Any]]:
        return tuple(self.records.get(record_type, []))


class FakeRecommendationProvider(RecommendationProvider):
    def generate(self, assessment: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "suggested_priority": "priority-a",
            "factors": ["heart_rate=110 bpm", "symptom=chest pain"],
            "warnings": ["prototype decision support"],
            "uncertainty": "available",
        }


class UnavailableRecommendationProvider(RecommendationProvider):
    def generate(self, assessment: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("provider unavailable")


class AlternatePriorityProvider(RecommendationProvider):
    def generate(self, assessment: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "suggested_priority": "priority-other",
            "factors": ["alternate opaque test factor"],
            "warnings": ["prototype decision support"],
            "uncertainty": "available",
        }


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> FakeRecordStore:
    value = FakeRecordStore()
    monkeypatch.setattr(api, "record_store", value)
    monkeypatch.setattr(api, "recommendation_provider", FakeRecommendationProvider())
    return value


def post_json(client: Client, path: str, payload: Mapping[str, Any]):
    return client.post(path, data=json.dumps(payload), content_type="application/json")


def put_json(client: Client, path: str, payload: Mapping[str, Any]):
    return client.put(path, data=json.dumps(payload), content_type="application/json")


def assessment_payload() -> dict[str, Any]:
    return {
        "nurse_id": "N-001",
        "assessment": {
            "symptoms": [{"name": "chest pain"}],
            "vital_signs": [
                {"type": "heart_rate", "value": 110, "unit": "bpm"}
            ],
            "observations": ["alert"],
        },
    }


def routing_payload() -> dict[str, Any]:
    return {
        "administrator_id": "ADM-001",
        "facilities": [
            {
                "facility_id": "F-1",
                "capacity_status": {
                    "available_spaces": 2,
                    "estimated_wait_minutes": 20,
                },
            },
            {
                "facility_id": "F-2",
                "capacity_status": {
                    "available_spaces": 1,
                    "estimated_wait_minutes": 10,
                },
            },
        ],
        "travel_times_minutes": {"F-1": 12, "F-2": 8},
    }


def seed_encounter(store: FakeRecordStore) -> None:
    store.save(
        "patient_encounter",
        {"id": "E-1001", "encounter_id": "E-1001", "status": "open"},
    )


def seed_assessment(store: FakeRecordStore) -> None:
    seed_encounter(store)
    store.save(
        "triage_assessment",
        {
            "id": "A-1001",
            "assessment_id": "A-1001",
            "encounter_id": "E-1001",
            "status": "stored",
        },
    )


def seed_recommendation(store: FakeRecordStore) -> None:
    seed_assessment(store)
    store.save(
        "urgency_recommendation",
        {
            "id": "R-1001",
            "recommendation_id": "R-1001",
            "encounter_id": "E-1001",
            "assessment_id": "A-1001",
            "suggested_priority": "priority-a",
            "advisory": True,
            "factors": ["heart_rate=110 bpm", "symptom=chest pain"],
            "warnings": ["prototype decision support"],
            "uncertainty": "available",
        },
    )


def seed_approved_priority(store: FakeRecordStore) -> None:
    seed_encounter(store)
    store.save(
        "triage_priority",
        {
            "id": "TP-1001",
            "encounter_id": "E-1001",
            "triage_priority": "priority-a",
        },
    )


def seed_waiting_encounter(store: FakeRecordStore) -> None:
    seed_approved_priority(store)
    store.save(
        "patient_queue",
        {"id": "Q-1001", "encounter_id": "E-1001", "status": "waiting"},
    )


def seed_routing_recommendation(store: FakeRecordStore) -> None:
    seed_approved_priority(store)
    store.save(
        "routing_recommendation",
        {
            "id": "RR-1001",
            "routing_recommendation_id": "RR-1001",
            "encounter_id": "E-1001",
            "advisory": True,
            "automatic_transfer": False,
            "considered_inputs": {
                "triage_priority": "priority-a",
                "facilities": routing_payload()["facilities"],
                "travel_times_minutes": routing_payload()["travel_times_minutes"],
            },
        },
    )


def records_snapshot(store: FakeRecordStore) -> dict[str, list[dict[str, Any]]]:
    return copy.deepcopy(store.records)


def test_AC_001_record_triage_assessment(client: Client, store: FakeRecordStore):
    seed_encounter(store)
    response = post_json(
        client, "/api/v1/encounters/E-1001/assessments", assessment_payload()
    )

    assert response.status_code == 201
    body = response.json()
    assert body["assessment_id"]
    assert body["encounter_id"] == "E-1001"
    assert body["status"] == "stored"
    assert len(store.list("triage_assessment")) == 1


def test_AC_002_display_advisory_recommendation(
    client: Client, store: FakeRecordStore
):
    seed_assessment(store)
    response = post_json(
        client,
        "/api/v1/encounters/E-1001/urgency-recommendations",
        {"assessment_id": "A-1001"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["recommendation_id"]
    assert body["encounter_id"] == "E-1001"
    assert body["assessment_id"] == "A-1001"
    assert body["suggested_priority"] == "priority-a"
    assert body["advisory"] is True
    assert store.list("triage_priority") == ()

    latest = client.get(
        "/api/v1/encounters/E-1001/urgency-recommendations/latest"
    )
    assert latest.status_code == 200
    assert latest.json()["recommendation_id"] == body["recommendation_id"]


def test_AC_002_outside_unknown_assessment_creates_nothing(
    client: Client, store: FakeRecordStore
):
    seed_encounter(store)
    before = records_snapshot(store)

    response = post_json(
        client,
        "/api/v1/encounters/E-1001/urgency-recommendations",
        {"assessment_id": "A-9999"},
    )

    assert store.records == before
    assert response.status_code == 404


def test_AC_003_explain_recommendation(client: Client, store: FakeRecordStore):
    seed_recommendation(store)
    before = records_snapshot(store)
    response = client.get(
        "/api/v1/encounters/E-1001/urgency-recommendations/R-1001/explanation"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendation_id"] == "R-1001"
    assert body["factors"] == ["heart_rate=110 bpm", "symptom=chest pain"]
    assert body["warnings"] == ["prototype decision support"]
    assert "uncertainty" in body
    assert store.records == before


def test_AC_003_outside_unknown_recommendation_changes_nothing(
    client: Client, store: FakeRecordStore
):
    seed_recommendation(store)
    before = records_snapshot(store)

    response = client.get(
        "/api/v1/encounters/E-1001/urgency-recommendations/R-9999/explanation"
    )

    assert store.records == before
    assert response.status_code == 404


def test_AC_004A_confirm_recommended_priority(
    client: Client, store: FakeRecordStore
):
    seed_recommendation(store)
    response = put_json(
        client,
        "/api/v1/encounters/E-1001/triage-priority",
        {
            "physician_id": "P-001",
            "recommended_priority": "priority-a",
            "selected_priority": "priority-a",
            "override_reason": None,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "encounter_id": "E-1001",
        "triage_priority": "priority-a",
        "override_reason": None,
        "queue_updated": True,
    }
    assert len(store.list("triage_priority")) == 1


def test_AC_004B_override_with_reason(client: Client, store: FakeRecordStore):
    seed_recommendation(store)
    reason = "clinical assessment indicates different urgency"
    response = put_json(
        client,
        "/api/v1/encounters/E-1001/triage-priority",
        {
            "physician_id": "P-001",
            "recommended_priority": "priority-a",
            "selected_priority": "priority-b",
            "override_reason": reason,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["triage_priority"] == "priority-b"
    assert body["override_reason"] == reason
    assert body["queue_updated"] is True
    assert len(store.list("triage_priority")) == 1


def test_AC_004C_reject_override_without_reason(
    client: Client, store: FakeRecordStore
):
    seed_recommendation(store)
    before = records_snapshot(store)
    response = put_json(
        client,
        "/api/v1/encounters/E-1001/triage-priority",
        {
            "physician_id": "P-001",
            "recommended_priority": "priority-a",
            "selected_priority": "priority-b",
        },
    )

    assert store.records == before
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "override_reason_required"
    assert body["message"]


def test_AC_004C_control_accept_override_with_reason(
    client: Client, store: FakeRecordStore
):
    seed_recommendation(store)
    response = put_json(
        client,
        "/api/v1/encounters/E-1001/triage-priority",
        {
            "physician_id": "P-001",
            "recommended_priority": "priority-a",
            "selected_priority": "priority-b",
            "override_reason": "clinical assessment indicates different urgency",
        },
    )

    assert response.status_code == 200
    assert response.json()["triage_priority"] == "priority-b"
    assert len(store.list("triage_priority")) == 1


def test_AC_004C_outside_empty_reason_changes_nothing(
    client: Client, store: FakeRecordStore
):
    seed_recommendation(store)
    before = records_snapshot(store)

    response = put_json(
        client,
        "/api/v1/encounters/E-1001/triage-priority",
        {
            "physician_id": "P-001",
            "recommended_priority": "priority-a",
            "selected_priority": "priority-b",
            "override_reason": "",
        },
    )

    assert store.records == before
    assert response.status_code == 422
    assert response.json()["error"] == "override_reason_required"
    assert response.json()["message"]


def test_AC_004C_inside_one_character_reason_is_accepted(
    client: Client, store: FakeRecordStore
):
    seed_recommendation(store)
    response = put_json(
        client,
        "/api/v1/encounters/E-1001/triage-priority",
        {
            "physician_id": "P-001",
            "recommended_priority": "priority-a",
            "selected_priority": "priority-b",
            "override_reason": "x",
        },
    )

    assert response.status_code == 200
    assert response.json()["triage_priority"] == "priority-b"
    assert response.json()["override_reason"] == "x"
    assert len(store.list("triage_priority")) == 1


def test_AC_005_reassess_waiting_patient(client: Client, store: FakeRecordStore):
    seed_waiting_encounter(store)
    response = post_json(
        client,
        "/api/v1/encounters/E-1001/reassessments",
        {
            "nurse_id": "N-001",
            "assessment": {
                "symptoms": [{"name": "chest pain", "changed": True}],
                "vital_signs": [
                    {"type": "heart_rate", "value": 125, "unit": "bpm"}
                ],
                "observations": ["condition changed"],
            },
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["assessment_id"]
    assert body["encounter_id"] == "E-1001"
    assert body["status"] == "stored"
    assert body["requires_priority_review"] is True
    assert body["prior_priority_unchanged"] is True
    assert len(store.list("triage_assessment")) == 1


def test_AC_005_outside_encounter_not_in_queue_creates_nothing(
    client: Client, store: FakeRecordStore
):
    seed_approved_priority(store)
    before = records_snapshot(store)

    response = post_json(
        client,
        "/api/v1/encounters/E-1001/reassessments",
        {
            "nurse_id": "N-001",
            "assessment": {
                "symptoms": [{"name": "chest pain", "changed": True}],
                "vital_signs": [
                    {"type": "heart_rate", "value": 125, "unit": "bpm"}
                ],
                "observations": ["condition changed"],
            },
        },
    )

    assert store.records == before
    assert response.status_code == 409


def test_AC_006_review_advisory_routing(client: Client, store: FakeRecordStore):
    seed_routing_recommendation(store)
    before = records_snapshot(store)
    response = client.get(
        "/api/v1/encounters/E-1001/routing-recommendations/latest"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["routing_recommendation_id"] == "RR-1001"
    assert body["encounter_id"] == "E-1001"
    assert body["advisory"] is True
    assert body["automatic_transfer"] is False
    assert "considered_inputs" in body
    assert store.list("patient_transfer") == ()
    assert store.records == before


def test_AC_006_outside_unknown_routing_recommendation_creates_nothing(
    client: Client, store: FakeRecordStore
):
    seed_approved_priority(store)
    before = records_snapshot(store)

    response = client.get(
        "/api/v1/encounters/E-1001/routing-recommendations/latest"
    )

    assert store.records == before
    assert response.status_code == 404


def test_AC_007_preserve_human_authority(client: Client, store: FakeRecordStore):
    seed_assessment(store)
    response = post_json(
        client,
        "/api/v1/encounters/E-1001/urgency-recommendations",
        {"assessment_id": "A-1001"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["advisory"] is True
    assert body["suggested_priority"] == "priority-a"
    assert store.list("triage_priority") == ()
    assert store.list("patient_queue") == ()


def test_AC_007_alternate_priority_is_not_approved_automatically(
    client: Client, store: FakeRecordStore, monkeypatch: pytest.MonkeyPatch
):
    seed_assessment(store)
    monkeypatch.setattr(api, "recommendation_provider", AlternatePriorityProvider())

    response = post_json(
        client,
        "/api/v1/encounters/E-1001/urgency-recommendations",
        {"assessment_id": "A-1001"},
    )

    assert response.status_code == 201
    assert response.json()["suggested_priority"] == "priority-other"
    assert response.json()["advisory"] is True
    assert store.list("triage_priority") == ()
    assert store.list("patient_queue") == ()


def test_AC_008_use_priority_capacity_and_travel_time(
    client: Client, store: FakeRecordStore
):
    seed_approved_priority(store)
    response = post_json(
        client,
        "/api/v1/encounters/E-1001/routing-recommendations",
        routing_payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["routing_recommendation_id"]
    assert body["encounter_id"] == "E-1001"
    assert body["advisory"] is True
    assert body["automatic_transfer"] is False
    assert body["considered_inputs"]["triage_priority"] == "priority-a"
    assert body["considered_inputs"]["facilities"] == routing_payload()["facilities"]
    assert body["considered_inputs"]["travel_times_minutes"] == {
        "F-1": 12,
        "F-2": 8,
    }
    assert store.list("patient_transfer") == ()


def test_AC_009_continue_when_ml_unavailable(
    client: Client, store: FakeRecordStore, monkeypatch: pytest.MonkeyPatch
):
    seed_assessment(store)
    before = records_snapshot(store)
    monkeypatch.setattr(api, "recommendation_provider", UnavailableRecommendationProvider())
    response = post_json(
        client,
        "/api/v1/encounters/E-1001/urgency-recommendations",
        {"assessment_id": "A-1001"},
    )

    assert store.records == before
    assert store.get("triage_assessment", "A-1001") is not None
    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "ml_unavailable"
    assert body["message"]


def test_AC_009_control_available_provider(
    client: Client, store: FakeRecordStore
):
    seed_assessment(store)
    response = post_json(
        client,
        "/api/v1/encounters/E-1001/urgency-recommendations",
        {"assessment_id": "A-1001"},
    )

    assert response.status_code == 201
    assert response.json()["advisory"] is True
    assert store.list("triage_priority") == ()
