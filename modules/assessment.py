from typing import Any
from uuid import uuid4

from modules import NotFoundError
from modules.access_control import authorize
from modules.data_store import DataStore


def save_assessment(
    encounter_id: str,
    user_id: str,
    data: dict[str, Any],
    store: DataStore,
) -> dict[str, Any]:
    authorize(user_id, "save_assessment", store)

    if not store.get_records("encounter", encounter_id):
        raise NotFoundError("The encounter was not found.")

    assessment_record = {**data, "encounter_id": encounter_id}

    if "assessment_id" not in assessment_record:
        assessment_record["assessment_id"] = str(uuid4())

    store.save_record("assessment", encounter_id, assessment_record)

    return assessment_record

def get_assessment(
    encounter_id: str,
    user_id: str,
    store: DataStore,
) -> dict[str, Any]:
    raise NotImplementedError("Retrieving assessments is not implemented yet.")