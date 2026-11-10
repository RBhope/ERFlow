from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any


class RecordStore(ABC):
    """Injected persistence contract for prototype records."""

    @abstractmethod
    def save(self, record_type: str, record: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get(self, record_type: str, record_id: str) -> Mapping[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def list(self, record_type: str) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError
