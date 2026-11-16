from typing import Any, Callable

from modules.data_store import DataStore
from modules import NotFoundError

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
    if not store.get_records("encounter", encounter_id):
        raise NotFoundError("The encounter was not found.")

    recommendations = store.get_records("recommendation", encounter_id)

    if not recommendations:
        raise NotFoundError("The recommendation was not found.")

    return recommendations[-1]