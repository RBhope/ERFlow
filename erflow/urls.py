from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from modules import user_interface


urlpatterns = [
    path(
        "api/encounters/<str:encounter_id>/assessments",
        csrf_exempt(user_interface.save_assessment),
    ),
    path(
        "api/encounters/<str:encounter_id>/assessment",
        csrf_exempt(user_interface.get_assessment),
    ),
    path(
        "api/encounters/<str:encounter_id>/recommendations",
        csrf_exempt(user_interface.generate_recommendation),
    ),
    path(
        "api/encounters/<str:encounter_id>/recommendation",
        csrf_exempt(user_interface.get_recommendation),
    ),
    path(
        "api/encounters/<str:encounter_id>/priority",
        csrf_exempt(user_interface.record_priority),
    ),
    path("api/queue", csrf_exempt(user_interface.get_queue)),
    path(
        "api/encounters/<str:encounter_id>/routing",
        csrf_exempt(user_interface.review_routing),
    ),
    path("api/facilities/capacity", csrf_exempt(user_interface.get_capacity)),
]