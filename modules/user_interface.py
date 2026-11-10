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
    return _not_implemented(
        lambda: assessment.save_assessment(encounter_id, "", {}, None)
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