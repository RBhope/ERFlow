from typing import Any

from modules import NotFoundError
from modules.access_control import authorize
from modules.data_store import DataStore


def record_priority(
    encounter_id: str,
    user_id: str,
    decision: dict[str, Any],
    store: DataStore,
) -> dict[str, Any]:
    authorize(user_id, "record_priority", store)

    if not store.get_records("encounter", encounter_id):
        raise NotFoundError("The encounter was not found.")

    recommendations = store.get_records("recommendation", encounter_id)
    if not recommendations:
        raise NotFoundError("The recommendation was not found.")

    recommended_priority = recommendations[-1]["priority"]
    action = decision.get("action")

    if action == "confirm":
        priority = recommended_priority
        override_reason = None
    elif action == "override":
        priority = decision.get("priority")
        override_reason = decision.get("override_reason")

        if not isinstance(priority, str) or not priority:
            raise ValueError("An override priority is required.")

        if priority == recommended_priority:
            raise ValueError("An override must select a different priority.")

        if not isinstance(override_reason, str) or not override_reason.strip():
            raise ValueError("An override reason is required.")
    else:
        raise ValueError("The action must be confirm or override.")

    priority_record = {
        "encounter_id": encounter_id,
        "priority": priority,
        "override_reason": override_reason,
    }

    queue_update = {
        "encounter_id": encounter_id,
        "priority": priority,
    }

    store.save_record("priority", encounter_id, priority_record)
    store.save_record("queue", "waiting", queue_update)

    return priority_record


def get_queue(
    user_id: str,
    store: DataStore,
) -> list[dict[str, Any]]:
    raise NotImplementedError("Retrieving the patient queue is not implemented yet.")