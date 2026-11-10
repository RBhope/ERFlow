from typing import Any

from modules.data_store import DataStore


def record_priority(
    encounter_id: str,
    user_id: str,
    decision: dict[str, Any],
    store: DataStore,
) -> dict[str, Any]:
    raise NotImplementedError("Recording priorities is not implemented yet.")


def get_queue(
    user_id: str,
    store: DataStore,
) -> list[dict[str, Any]]:
    raise NotImplementedError("Retrieving the patient queue is not implemented yet.")
