from typing import Any


def save_record(kind: str, encounter_id: str, record: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError("Saving records is not implemented yet.")


def get_records(kind: str, encounter_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError("Retrieving records is not implemented yet.")


def get_role(user_id: str) -> str:
    raise NotImplementedError("Retrieving user roles is not implemented yet.")


def get_facilities() -> list[dict[str, Any]]:
    raise NotImplementedError("Retrieving facilities is not implemented yet.")

from typing import Protocol


class DataStore(Protocol):
    def save_record(
        self, kind: str, encounter_id: str, record: dict[str, Any]
    ) -> dict[str, Any]:
        raise NotImplementedError

    def get_records(self, kind: str, encounter_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_role(self, user_id: str) -> str:
        raise NotImplementedError

    def get_facilities(self) -> list[dict[str, Any]]:
        raise NotImplementedError
