from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from erflow.modules.data_store import RecordStore


class RecommendationProvider(ABC):
    """Injected urgency-recommendation provider, real or simulated."""

    @abstractmethod
    def generate(self, assessment: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError


def generate_urgency_recommendation(
    *,
    encounter_id: str,
    assessment_id: str,
    provider: RecommendationProvider,
    store: RecordStore,
) -> Mapping[str, Any]:
    """Generate and store an advisory UrgencyRecommendation."""
    raise NotImplementedError


def get_urgency_recommendation(
    *, encounter_id: str, store: RecordStore
) -> Mapping[str, Any]:
    """Return the latest advisory UrgencyRecommendation for review."""
    raise NotImplementedError


def get_recommendation_explanation(
    *, encounter_id: str, recommendation_id: str, store: RecordStore
) -> Mapping[str, Any]:
    """Return factors, warnings, and uncertainty for a recommendation."""
    raise NotImplementedError
