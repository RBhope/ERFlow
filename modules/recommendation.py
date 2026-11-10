from typing import Any, Callable

from modules.data_store import DataStore


RecommendationProvider = Callable[[dict[str, Any]], dict[str, Any]]


def generate_recommendation(
    encounter_id: str,
    user_id: str,
    store: DataStore,
    provider: RecommendationProvider,
) -> dict[str, Any]:
    raise NotImplementedError("Generating recommendations is not implemented yet.")


def get_recommendation(
    encounter_id: str,
    user_id: str,
    store: DataStore,
) -> dict[str, Any]:
    raise NotImplementedError("Retrieving recommendations is not implemented yet.")
