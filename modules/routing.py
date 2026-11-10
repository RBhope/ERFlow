from typing import Any

from modules.data_store import DataStore


def review_routing(
    encounter_id: str,
    user_id: str,
    store: DataStore,
) -> dict[str, Any]:
    raise NotImplementedError("Routing review is not implemented yet.")


def get_capacity(
    user_id: str,
    store: DataStore,
) -> list[dict[str, Any]]:
    raise NotImplementedError("Retrieving capacity is not implemented yet.")