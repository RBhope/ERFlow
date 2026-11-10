# ERFlow Contracts

## Purpose

This document describes the proposed functions and API routes for the ERFlow course prototype. It is based on `spec.md` and `architecture.md` and will guide the code skeleton and tests. The API paths, field names, and status codes are design choices for the prototype.

The prototype uses synthetic patient data. Recommendations are advisory, and a simulated provider can be used to test the workflow. A simulation alone does not fulfill the ML requirement in FR-007.

## Shared conventions

- Encounter, user, and facility IDs are strings. `E1` and `F1` are examples of synthetic test IDs.
- API responses use JSON. `advisory` is a Boolean. The allowed priority levels, their order, and the routing algorithm have not been defined yet.
- Requests use an `X-User-Id` header to identify a preconfigured synthetic test user. This is a testing convention, not secure authentication. The actual authentication method remains open; role restrictions follow NFR-002.
- Errors use `{"error": "<code>", "message": "<description>"}`. Proposed codes are `403 forbidden` for an unauthorized action, `404 not_found` for an unknown encounter, and `503 recommendation_unavailable` for provider failure. A rejected request creates no record and changes no existing record. A provider failure after a successful assessment save is a separate case: the saved assessment must remain available (NFR-004).
- In the initial skeleton, business functions raise `NotImplementedError` and each listed API route returns HTTP `501` with `{"error": "not_implemented", "message": "..."}`. The success and error results below describe the behavior to implement later.

## Public module functions

The functions use the JSON-compatible data types defined below. `store` and `provider` are dependencies supplied to the functions. The table shows the intended results once the behavior is implemented.

| Module and signature | Success result | Intended failures and injected dependencies | Trace |
| --- | --- | --- | --- |
| Access Control: `authorize(user_id: str, action: str, store: DataStore) -> None` | Returns normally when the role is permitted. | Unauthorized action: `ForbiddenError`. Injected: `store` for role lookup. | NFR-002 |
| Assessment: `save_assessment(encounter_id: str, user_id: str, data: Assessment, store: DataStore) -> Assessment` | Returns the saved assessment associated with the encounter. Also used for reassessment. | Unauthorized: `ForbiddenError`; unknown encounter: `NotFoundError`; storage failure: `StorageError`, with recovery behavior open. Injected: `store`. | FR-001, FR-005; AC-001, AC-007; NFR-003 |
| Assessment: `get_assessment(encounter_id: str, user_id: str, store: DataStore) -> Assessment` | Returns the latest saved assessment for the encounter. | Unknown encounter or assessment: `NotFoundError`; unauthorized: `ForbiddenError`. Injected: `store`. Returning the latest assessment is a contract choice; history requirements remain open. | FR-001, FR-005; NFR-003 |
| Recommendation: `generate_recommendation(encounter_id: str, user_id: str, store: DataStore, provider: RecommendationProvider) -> Recommendation` | Returns an advisory recommendation and contributing factors for the saved assessment. | Provider failure: `RecommendationUnavailableError`; a successfully saved assessment remains available and clinical priority is unchanged. Injected: `store`, `provider`. | FR-002, FR-003, FR-007; AC-002, AC-003, AC-007; NFR-004, NFR-005, NFR-007 |
| Recommendation: `get_recommendation(encounter_id: str, user_id: str, store: DataStore) -> Recommendation` | Returns the current advisory recommendation and factors. | Missing encounter or recommendation: `NotFoundError`. Injected: `store`. | FR-002, FR-003; AC-003, AC-009 |
| Priority and Queue: `record_priority(encounter_id: str, user_id: str, decision: PriorityDecision, store: DataStore) -> PriorityDecision` | Returns the saved clinician decision; an override includes its reason. The queue reflects the decision. | Unauthorized: `ForbiddenError`; unknown encounter: `NotFoundError`; other invalid-state and storage behavior remains open. Injected: `store`. | FR-004, FR-005; AC-004, AC-005; NFR-001, NFR-003 |
| Priority and Queue: `get_queue(user_id: str, store: DataStore) -> list[QueueEntry]` | Returns waiting encounters and their current priorities. | Failure behavior and exact ordering remain open. Injected: `store`. | FR-005; AC-006 |
| Routing: `review_routing(encounter_id: str, user_id: str, store: DataStore) -> Routing` | Returns an advisory facility recommendation and the priority, capacity, and travel-time values used. | Unauthorized: `ForbiddenError`; unknown encounter: `NotFoundError`; missing or stale inputs and ranking are open. Injected: `store`. | FR-006, FR-008; AC-008, AC-010 |
| Routing: `get_capacity(user_id: str, store: DataStore) -> list[Capacity]` | Returns available facility-capacity data. | Unauthorized access or unavailable data behavior for this read remains open. Injected: `store`. | FR-006 |
| Data Store: `save_record(kind: str, encounter_id: str, record: Record) -> Record` | Returns the saved record associated with the encounter. | Storage failure: `StorageError`; atomicity and recovery are open. No explicit injection. | AC-001, AC-004, AC-005, AC-007; NFR-003 |
| Data Store: `get_records(kind: str, encounter_id: str) -> list[Record]` | Returns matching records for the encounter. | Storage failure: `StorageError`; missing-record behavior remains open. No explicit injection. | NFR-003 |

### Supporting types and interfaces

The following are interface definitions for the modules above. They do not add new architectural modules.

```python
from typing import Callable, Protocol, TypeAlias

Record: TypeAlias = dict[str, object]
Assessment: TypeAlias = dict[str, object]
Recommendation: TypeAlias = dict[str, object]
PriorityDecision: TypeAlias = dict[str, object]
QueueEntry: TypeAlias = dict[str, object]
Capacity: TypeAlias = dict[str, object]
Routing: TypeAlias = dict[str, object]
RecommendationProvider: TypeAlias = Callable[[Assessment], Recommendation]

class DataStore(Protocol):
    def save_record(self, kind: str, encounter_id: str, record: Record) -> Record: ...
    def get_records(self, kind: str, encounter_id: str) -> list[Record]: ...
    def get_role(self, user_id: str) -> str: ...
    def get_facilities(self) -> list[Capacity]: ...
```

`get_role` supports Access Control and `get_facilities` supplies Routing. Both are public Data Store functions and will raise `NotImplementedError` in the skeleton. `get_role` returns the user's modeled role; unknown-user behavior is not specified. `get_facilities` returns synthetic capacity records; unavailable-data behavior is not specified. These functions serve NFR-002 and FR-006/FR-008, respectively. No clock is injected; the test harness measures the response-time target in NFR-006.

The proposed exception types are `ForbiddenError`, `NotFoundError`, `StorageError`, and `RecommendationUnavailableError`. The skeleton needs to define these types before tests import them; the rules for precedence and storage recovery are still open.

## REST API contracts

The User Interface module contains the HTTP handlers. Each route maps to the function shown below. The paths, methods, and future response codes are proposed choices for the prototype.

| Method and path | Public function | Target response | Trace |
| --- | --- | --- | --- |
| `POST /api/encounters/{encounter_id}/assessments` | `assessment.save_assessment` | `201`: `{"encounter_id":"E1", "assessment_id":"A1", "assessment":{...}}` | FR-001, FR-005; AC-001, AC-007 |
| `GET /api/encounters/{encounter_id}/assessment` | `assessment.get_assessment` | `200`: `{"encounter_id":"E1", "assessment_id":"A1", "assessment":{...}}` | FR-001, FR-005; NFR-003 |
| `POST /api/encounters/{encounter_id}/recommendations` | `recommendation.generate_recommendation` | `200`: `{"encounter_id":"E1", "priority":"TEST-PRIORITY-A", "advisory":true, "factors":["dizziness"]}` | FR-002, FR-003, FR-007; AC-002, AC-007; NFR-004 |
| `GET /api/encounters/{encounter_id}/recommendation` | `recommendation.get_recommendation` | `200`: same recommendation fields, including `advisory` and `factors` | FR-002, FR-003; AC-003, AC-009 |
| `POST /api/encounters/{encounter_id}/priority` | `priority_queue.record_priority` | `200`: `{"encounter_id":"E1", "priority":"TEST-PRIORITY-B", "override_reason":"Clinical assessment"}`; confirmation uses `null` for `override_reason` | FR-004; AC-004, AC-005 |
| `GET /api/queue` | `priority_queue.get_queue` | `200`: `{"encounters":[{"encounter_id":"E1", "priority":"TEST-PRIORITY-A"}]}` | FR-005; AC-006 |
| `POST /api/encounters/{encounter_id}/routing` | `routing.review_routing` | `200`: `{"encounter_id":"E1", "facility_id":"F1", "advisory":true, "priority":"TEST-PRIORITY-A", "capacity":{"available_spaces":2}, "travel_time_minutes":10}` | FR-006, FR-008; AC-008, AC-010 |
| `GET /api/facilities/capacity` | `routing.get_capacity` | `200`: `{"facilities":[{"facility_id":"F1", "available_spaces":2}]}` | FR-006 |

### Example request bodies

- Assessment: `{"assessment_id":"A1", "complaint":"headache", "symptoms":["dizziness"], "vitals":{"heart_rate_bpm":90}}`. Reassessment uses the same route with a new assessment ID. These examples do not establish required fields or clinical ranges.
- Priority confirmation: `{"action":"confirm"}`. Override: `{"action":"override", "priority":"TEST-PRIORITY-B", "override_reason":"Clinical assessment"}`.
- Recommendation and routing requests use the saved encounter and have no request body in this proposed interface.

Priority ordering, routing selection, field validation, and simultaneous updates remain open. The system must not automatically assign a final priority or initiate a transfer (AC-008, AC-009).

## Starting the skeleton

The proposed implementation uses Python and Django. From the project folder:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py runserver
```

These commands must be checked against the completed skeleton before submission.
