from typing import Any

from modules.data_store import DataStore


def save_assessment(
    encounter_id: str,
    user_id: str,
    data: dict[str, Any],
    store: DataStore,
) -> dict[str, Any]:
    raise NotImplementedError("Saving assessments is not implemented yet.")


def get_assessment(
    encounter_id: str,
    user_id: str,
    store: DataStore,
) -> dict[str, Any]:
    raise NotImplementedError("Retrieving assessments is not implemented yet.")
