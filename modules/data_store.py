import json
import sqlite3
from contextlib import closing
from typing import Any, Protocol

from django.conf import settings

from modules import StorageError


def save_record(
    kind: str, encounter_id: str, record: dict[str, Any]
) -> dict[str, Any]:
    try:
        with closing(sqlite3.connect(settings.DATABASES["default"]["NAME"])) as connection:
            with connection:
                connection.execute(
                    "INSERT INTO records (kind, record_key, data) VALUES (?, ?, ?)",
                    (kind, encounter_id, json.dumps(record)),
                )
    except (sqlite3.Error, TypeError, ValueError) as exc:
        raise StorageError("The record could not be saved.") from exc

    return record


def get_records(kind: str, encounter_id: str) -> list[dict[str, Any]]:
    try:
        with closing(sqlite3.connect(settings.DATABASES["default"]["NAME"])) as connection:
            rows = connection.execute(
                "SELECT data FROM records WHERE kind = ? AND record_key = ? "
                "ORDER BY rowid",
                (kind, encounter_id),
            ).fetchall()

        return [json.loads(row[0]) for row in rows]
    except (sqlite3.Error, ValueError) as exc:
        raise StorageError("The records could not be retrieved.") from exc


def get_role(user_id: str) -> str:
    users = get_records("user", user_id)
    if not users:
        return ""

    return users[-1].get("role", "")


def get_facilities() -> list[dict[str, Any]]:
    raise NotImplementedError("Retrieving facilities is not implemented yet.")


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