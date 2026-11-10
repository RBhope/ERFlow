from collections.abc import Mapping
from typing import Any

from erflow.modules.data_store import RecordStore


def record_assessment(
    *,
    encounter_id: str,
    nurse_id: str,
    assessment: Mapping[str, Any],
    store: RecordStore,
) -> Mapping[str, Any]:
    """Store an initial TriageAssessment for a PatientEncounter."""
    raise NotImplementedError


def record_reassessment(
    *,
    encounter_id: str,
    nurse_id: str,
    assessment: Mapping[str, Any],
    store: RecordStore,
) -> Mapping[str, Any]:
    """Store an updated TriageAssessment without changing approved priority."""
    raise NotImplementedError
