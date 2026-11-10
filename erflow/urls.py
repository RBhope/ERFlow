from django.urls import path

from erflow import api

urlpatterns = [
    path(
        "api/v1/encounters/<str:encounter_id>/assessments",
        api.record_assessment,
        name="record-assessment",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/reassessments",
        api.record_reassessment,
        name="record-reassessment",
    ),
    path(
        "api/v1/patient-queue",
        api.patient_queue,
        name="patient-queue",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/urgency-recommendations",
        api.generate_urgency_recommendation,
        name="generate-urgency-recommendation",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/urgency-recommendations/latest",
        api.latest_urgency_recommendation,
        name="latest-urgency-recommendation",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/urgency-recommendations/"
        "<str:recommendation_id>/explanation",
        api.recommendation_explanation,
        name="recommendation-explanation",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/triage-priority",
        api.triage_priority,
        name="triage-priority",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/routing-recommendations",
        api.generate_routing_recommendation,
        name="generate-routing-recommendation",
    ),
    path(
        "api/v1/encounters/<str:encounter_id>/routing-recommendations/latest",
        api.latest_routing_recommendation,
        name="latest-routing-recommendation",
    ),
]
