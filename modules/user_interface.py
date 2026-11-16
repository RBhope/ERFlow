import json

from modules import ForbiddenError, NotFoundError, StorageError
from modules import data_store
from django.http import JsonResponse

from modules import assessment
from modules import priority_queue
from modules import recommendation
from modules import routing


def _not_implemented(call):
    try:
        call()
    except NotImplementedError:
        return JsonResponse(
            {
                "error": "not_implemented",
                "message": "This functionality is not implemented yet.",
            },
            status=501,
        )


def save_assessment(request, encounter_id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "method_not_allowed", "message": "Use POST for this route."},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "invalid_json", "message": "Provide a valid JSON object."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "invalid_json", "message": "Provide a JSON object."},
            status=400,
        )

    user_id = request.headers.get("X-User-Id", "")

    try:
        saved = assessment.save_assessment(
            encounter_id, user_id, data, data_store
        )
    except ForbiddenError:
        return JsonResponse(
            {"error": "forbidden", "message": "User is not authorized."},
            status=403,
        )
    except NotFoundError:
        return JsonResponse(
            {"error": "not_found", "message": "Encounter was not found."},
            status=404,
        )
    except StorageError:
        return JsonResponse(
            {"error": "storage_error", "message": "Assessment could not be saved."},
            status=500,
        )

    return JsonResponse(
        {
            "encounter_id": encounter_id,
            "assessment_id": saved["assessment_id"],
            "assessment": saved,
        },
        status=201,
    )


def get_assessment(request, encounter_id):
    return _not_implemented(
        lambda: assessment.get_assessment(encounter_id, "", None)
    )


def generate_recommendation(request, encounter_id):
    return _not_implemented(
        lambda: recommendation.generate_recommendation(
            encounter_id, "", None, lambda data: {}
        )
    )


def get_recommendation(request, encounter_id):
    return _not_implemented(
        lambda: recommendation.get_recommendation(encounter_id, "", None)
    )


def record_priority(request, encounter_id):
    return _not_implemented(
        lambda: priority_queue.record_priority(encounter_id, "", {}, None)
    )


def get_queue(request):
    return _not_implemented(
        lambda: priority_queue.get_queue("", None)
    )


def review_routing(request, encounter_id):
    return _not_implemented(
        lambda: routing.review_routing(encounter_id, "", None)
    )


def get_capacity(request):
    return _not_implemented(
        lambda: routing.get_capacity("", None)
    )