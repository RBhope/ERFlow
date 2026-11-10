from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from erflow.modules.data_store import RecordStore


def record_priority_decision(
    *,
    encounter_id: str,
    physician_id: str,
    selected_priority: str,
    recommended_priority: str | None,
    override_reason: str | None,
    store: RecordStore,
) -> Mapping[str, Any]:
    """Save a physician-confirmed or physician-overridden TriagePriority."""
    raise NotImplementedError


def list_patient_queue(
    *, requester_id: str, requester_role: str, store: RecordStore
) -> Sequence[Mapping[str, Any]]:
    """Return the waiting-patient view ordered by approved TriagePriority."""
    raise NotImplementedError
