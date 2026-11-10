"""HTTP transport for the ERFlow contract skeleton; contains no business logic."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Optional, cast

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from erflow.modules import assessment, priority_queue, recommendation, routing
from erflow.modules.data_store import RecordStore
from erflow.modules.recommendation import RecommendationProvider

# Injection points for a future composition root and for contract-level tests.
record_store: RecordStore | None = None
recommendation_provider: RecommendationProvider | None = None


def _payload(request: HttpRequest) -> Mapping[str, Any]:
    if not request.body:
        return {}
    try:
        value = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _store() -> RecordStore:
    return cast(RecordStore, record_store)


def _provider() -> RecommendationProvider:
    return cast(RecommendationProvider, recommendation_provider)


def _not_implemented(message: str) -> JsonResponse:
    return JsonResponse(
        {"error": "not_implemented", "message": message}, status=501
    )


@csrf_exempt
def record_assessment(request: HttpRequest, encounter_id: str) -> JsonResponse:
    payload = _payload(request)
    try:
        result = assessment.record_assessment(
            encounter_id=encounter_id,
            nurse_id=str(payload.get("nurse_id", "")),
            assessment=cast(Mapping[str, Any], payload.get("assessment", {})),
            store=_store(),
        )
        return JsonResponse(dict(result), status=201)
    except NotImplementedError:
        return _not_implemented("FR-001 record assessment is not implemented")


@csrf_exempt
def record_reassessment(request: HttpRequest, encounter_id: str) -> JsonResponse:
    payload = _payload(request)
    try:
        result = assessment.record_reassessment(
            encounter_id=encounter_id,
            nurse_id=str(payload.get("nurse_id", "")),
            assessment=cast(Mapping[str, Any], payload.get("assessment", {})),
            store=_store(),
        )
        return JsonResponse(dict(result), status=201)
    except NotImplementedError:
        return _not_implemented("FR-005 reassessment is not implemented")


def patient_queue(request: HttpRequest) -> JsonResponse:
    try:
        result = priority_queue.list_patient_queue(
            requester_id=request.headers.get("X-Actor-ID", ""),
            requester_role=request.headers.get("X-Actor-Role", ""),
            store=_store(),
        )
        return JsonResponse({"items": list(result)}, status=200)
    except NotImplementedError:
        return _not_implemented("FR-005 patient queue is not implemented")


@csrf_exempt
def generate_urgency_recommendation(
    request: HttpRequest, encounter_id: str
) -> JsonResponse:
    payload = _payload(request)
    try:
        result = recommendation.generate_urgency_recommendation(
            encounter_id=encounter_id,
            assessment_id=str(payload.get("assessment_id", "")),
            provider=_provider(),
            store=_store(),
        )
        return JsonResponse(dict(result), status=201)
    except NotImplementedError:
        return _not_implemented("FR-007 urgency processing is not implemented")


def latest_urgency_recommendation(
    request: HttpRequest, encounter_id: str
) -> JsonResponse:
    try:
        result = recommendation.get_urgency_recommendation(
            encounter_id=encounter_id, store=_store()
        )
        return JsonResponse(dict(result), status=200)
    except NotImplementedError:
        return _not_implemented("FR-002 recommendation review is not implemented")


def recommendation_explanation(
    request: HttpRequest, encounter_id: str, recommendation_id: str
) -> JsonResponse:
    try:
        result = recommendation.get_recommendation_explanation(
            encounter_id=encounter_id,
            recommendation_id=recommendation_id,
            store=_store(),
        )
        return JsonResponse(dict(result), status=200)
    except NotImplementedError:
        return _not_implemented("FR-003 recommendation explanation is not implemented")


@csrf_exempt
def triage_priority(request: HttpRequest, encounter_id: str) -> JsonResponse:
    payload = _payload(request)
    try:
        result = priority_queue.record_priority_decision(
            encounter_id=encounter_id,
            physician_id=str(payload.get("physician_id", "")),
            selected_priority=str(payload.get("selected_priority", "")),
            recommended_priority=cast(
                Optional[str], payload.get("recommended_priority")
            ),
            override_reason=cast(Optional[str], payload.get("override_reason")),
            store=_store(),
        )
        return JsonResponse(dict(result), status=200)
    except NotImplementedError:
        return _not_implemented("FR-004 priority decision is not implemented")


@csrf_exempt
def generate_routing_recommendation(
    request: HttpRequest, encounter_id: str
) -> JsonResponse:
    payload = _payload(request)
    try:
        result = routing.generate_routing_recommendation(
            encounter_id=encounter_id,
            administrator_id=str(payload.get("administrator_id", "")),
            facilities=cast(
                list[Mapping[str, Any]], payload.get("facilities", [])
            ),
            travel_times_minutes=cast(
                Mapping[str, int], payload.get("travel_times_minutes", {})
            ),
            store=_store(),
        )
        return JsonResponse(dict(result), status=201)
    except NotImplementedError:
        return _not_implemented("FR-008 routing generation is not implemented")


def latest_routing_recommendation(
    request: HttpRequest, encounter_id: str
) -> JsonResponse:
    try:
        result = routing.get_routing_recommendation(
            encounter_id=encounter_id, store=_store()
        )
        return JsonResponse(dict(result), status=200)
    except NotImplementedError:
        return _not_implemented("FR-006 routing review is not implemented")
