from collections.abc import Mapping, Sequence
from typing import Any

from erflow.modules.data_store import RecordStore


def generate_routing_recommendation(
    *,
    encounter_id: str,
    administrator_id: str,
    facilities: Sequence[Mapping[str, Any]],
    travel_times_minutes: Mapping[str, int],
    store: RecordStore,
) -> Mapping[str, Any]:
    """Generate and store an advisory RoutingRecommendation."""
    raise NotImplementedError


def get_routing_recommendation(
    *, encounter_id: str, store: RecordStore
) -> Mapping[str, Any]:
    """Return the latest advisory RoutingRecommendation for human review."""
    raise NotImplementedError
