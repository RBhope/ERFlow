# ERFlow Contracts

This document fixes the callable interfaces for the test-first skeleton. It does
not define business logic. Identifiers are opaque strings because `spec.md` does
not define identifier formats. Priority values are also opaque strings because
the specification does not define a priority scale or ordering.

## Python module contracts

All functions currently raise `NotImplementedError`. Future implementations
must preserve these signatures unless the specification and this contract are
updated together.

### User Interface

#### `present_workflow(*, workflow: str, context: Mapping[str, Any]) -> str`

- **Success result:** Rendered workflow content.
- **Failures:** Unknown workflow or unrenderable context; exact error behavior is
  not defined by the current specification.
- **Serves:** FR-001 through FR-006; User Interface module responsibility.
- **Injected:** The complete context is supplied by the caller. No clock is used.

### Access Control

#### `authorize(*, actor_id: str, actor_role: str, action: str, store: RecordStore) -> None`

- **Success result:** Returns `None` when the actor may perform the action.
- **Failures:** Unauthorized actor or role. Authentication and identity formats
  remain a spec gap.
- **Serves:** The authorized-role rules stated in the Domain Model and
  architecture.
- **Injected:** `RecordStore`. No clock is used.

### Assessment

#### `record_assessment(*, encounter_id: str, nurse_id: str, assessment: Mapping[str, Any], store: RecordStore) -> Mapping[str, Any]`

- **Success result:** A stored assessment representation containing at least
  `assessment_id`, `encounter_id`, and `status: "stored"`.
- **Failures:** Unauthorized role, unknown encounter, invalid assessment, or
  persistence failure. Required assessment fields are a spec gap.
- **Serves:** FR-001 and AC-001.
- **Injected:** `RecordStore`. No clock is used.

#### `record_reassessment(*, encounter_id: str, nurse_id: str, assessment: Mapping[str, Any], store: RecordStore) -> Mapping[str, Any]`

- **Success result:** A stored reassessment representation containing at least
  `assessment_id`, `encounter_id`, `status: "stored"`,
  `requires_priority_review: true`, and `prior_priority_unchanged: true`.
- **Failures:** Unauthorized role, unknown/nonwaiting encounter, invalid
  assessment, or persistence failure.
- **Serves:** FR-005 and AC-005.
- **Injected:** `RecordStore`. No clock is used.

### Recommendation

#### `RecommendationProvider.generate(assessment: Mapping[str, Any]) -> Mapping[str, Any]`

- **Success result:** Provider result containing a suggested priority, factors,
  warnings, and available uncertainty information.
- **Failures:** Provider unavailable or unable to process the assessment.
- **Serves:** FR-007 and the substitutable-provider design decision.
- **Injected:** The provider itself is injected into recommendation generation.
  No clock is used.

#### `generate_urgency_recommendation(*, encounter_id: str, assessment_id: str, provider: RecommendationProvider, store: RecordStore) -> Mapping[str, Any]`

- **Success result:** An advisory recommendation containing at least
  `recommendation_id`, `encounter_id`, `assessment_id`, `advisory: true`, and
  `suggested_priority`; it does not create a `TriagePriority`.
- **Failures:** Unknown encounter/assessment, invalid assessment state,
  recommendation provider unavailable, or persistence failure.
- **Serves:** FR-007, AC-002, AC-007, and AC-009.
- **Injected:** `RecommendationProvider` and `RecordStore`. No clock is used.

#### `get_urgency_recommendation(*, encounter_id: str, store: RecordStore) -> Mapping[str, Any]`

- **Success result:** Latest advisory recommendation with `advisory: true` and
  no claim that the suggested value is an approved `TriagePriority`.
- **Failures:** Unknown encounter or no recommendation available.
- **Serves:** FR-002 and AC-002.
- **Injected:** `RecordStore`. No clock is used.

#### `get_recommendation_explanation(*, encounter_id: str, recommendation_id: str, store: RecordStore) -> Mapping[str, Any]`

- **Success result:** `recommendation_id`, `factors`, `warnings`, and
  `uncertainty` fields.
- **Failures:** Unknown encounter or recommendation.
- **Serves:** FR-003 and AC-003.
- **Injected:** `RecordStore`. No clock is used.

### Priority and Queue

#### `record_priority_decision(*, encounter_id: str, physician_id: str, selected_priority: str, recommended_priority: str | None, override_reason: str | None, store: RecordStore) -> Mapping[str, Any]`

- **Success result:** `encounter_id`, `triage_priority`, `override_reason`, and
  `queue_updated: true`.
- **Failures:** Unauthorized role, unknown encounter, unavailable recommendation
  when confirmation is attempted, missing override reason when selected and
  recommended priorities differ, invalid priority, conflict, or persistence
  failure. Priority values and concurrency policy are spec gaps.
- **Serves:** FR-004, AC-004A, AC-004B, and AC-004C.
- **Injected:** `RecordStore`. No clock is used.

#### `list_patient_queue(*, requester_id: str, requester_role: str, store: RecordStore) -> Sequence[Mapping[str, Any]]`

- **Success result:** Waiting encounters and their approved priorities, ordered
  by the specification's priority rule.
- **Failures:** Unauthorized role or persistence failure. The priority ordering
  is a spec gap, so exact ordering cannot yet be asserted.
- **Serves:** FR-005 and the `PatientQueue` domain rule.
- **Injected:** `RecordStore`. No clock is used.

### Routing

#### `generate_routing_recommendation(*, encounter_id: str, administrator_id: str, facilities: Sequence[Mapping[str, Any]], travel_times_minutes: Mapping[str, int], store: RecordStore) -> Mapping[str, Any]`

- **Success result:** An advisory result containing `routing_recommendation_id`,
  `encounter_id`, `advisory: true`, `considered_inputs`, and
  `automatic_transfer: false`.
- **Failures:** Unauthorized role, unknown encounter, missing approved priority,
  missing or invalid routing inputs, or persistence failure. Facility ranking
  and stale/missing input behavior are spec gaps.
- **Serves:** FR-008 and AC-008.
- **Injected:** `RecordStore`; facilities and travel times are explicit inputs.
  No clock is used because the spec defines no freshness rule.

#### `get_routing_recommendation(*, encounter_id: str, store: RecordStore) -> Mapping[str, Any]`

- **Success result:** Latest advisory routing result, the inputs used, and
  `automatic_transfer: false`.
- **Failures:** Unknown encounter or no routing recommendation available.
- **Serves:** FR-006 and AC-006.
- **Injected:** `RecordStore`. No clock is used.

### Data Store

#### `RecordStore.save(record_type: str, record: Mapping[str, Any]) -> Mapping[str, Any]`

- **Success result:** The stored representation.
- **Failures:** Persistence failure.
- **Serves:** Architecture Data Store responsibility.
- **Injected:** Concrete store implementation. No clock is used.

#### `RecordStore.get(record_type: str, record_id: str) -> Mapping[str, Any] | None`

- **Success result:** The matching record or `None`.
- **Failures:** Persistence failure.
- **Serves:** Architecture Data Store responsibility.
- **Injected:** Concrete store implementation. No clock is used.

#### `RecordStore.list(record_type: str) -> Sequence[Mapping[str, Any]]`

- **Success result:** All matching prototype records.
- **Failures:** Persistence failure.
- **Serves:** Architecture Data Store responsibility and queue listing.
- **Injected:** Concrete store implementation. No clock is used.

## REST API contracts

All routes accept and return JSON. Until business logic is implemented, every
route returns HTTP `501` with:

```json
{"error": "not_implemented", "message": "..."}
```

The success and domain-error statuses below are the target contracts for tests.
They refine the acceptance criteria but do not resolve the listed spec gaps.

| Requirement | Method and route | Public function | Target success | Target domain failures |
| --- | --- | --- | --- | --- |
| FR-001 | `POST /api/v1/encounters/{encounter_id}/assessments` | `assessment.record_assessment` | `201`; assessment fields listed above | `403` unauthorized; `404` encounter; `422` invalid assessment; `500` persistence |
| FR-002 | `GET /api/v1/encounters/{encounter_id}/urgency-recommendations/latest` | `recommendation.get_urgency_recommendation` | `200`; advisory recommendation | `404` encounter/recommendation |
| FR-003 | `GET /api/v1/encounters/{encounter_id}/urgency-recommendations/{recommendation_id}/explanation` | `recommendation.get_recommendation_explanation` | `200`; factors/warnings/uncertainty | `404` encounter/recommendation |
| FR-004 | `PUT /api/v1/encounters/{encounter_id}/triage-priority` | `priority_queue.record_priority_decision` | `200`; approved priority and queue update | `403`, `404`, `409`, `422 override_reason_required`, `500` |
| FR-005 | `POST /api/v1/encounters/{encounter_id}/reassessments` | `assessment.record_reassessment` | `201`; saved reassessment with review flags | `403`, `404`, `409`, `422`, `500` |
| FR-005 | `GET /api/v1/patient-queue` | `priority_queue.list_patient_queue` | `200`; `{ "items": [...] }` | `403`, `500` |
| FR-006 | `GET /api/v1/encounters/{encounter_id}/routing-recommendations/latest` | `routing.get_routing_recommendation` | `200`; advisory routing result and inputs | `404` encounter/recommendation |
| FR-007 | `POST /api/v1/encounters/{encounter_id}/urgency-recommendations` | `recommendation.generate_urgency_recommendation` | `201`; advisory recommendation, no priority side effect | `404`, `409`, `422`, `503 ml_unavailable`, `500` |
| FR-008 | `POST /api/v1/encounters/{encounter_id}/routing-recommendations` | `routing.generate_routing_recommendation` | `201`; advisory result, considered inputs, no transfer | `403`, `404`, `409`, `422`, `500` |

Role identity is carried as `X-Actor-ID` and `X-Actor-Role` for GET routes and
as the role-specific actor ID in POST/PUT bodies. This is only a prototype
calling convention; authentication remains a spec gap.

## Start commands

```bash
cd /Users/rajasbhope/Downloads/SoftwareDesign/ERFlow
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py runserver
```
