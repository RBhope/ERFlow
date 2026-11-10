# ERFlow Test Plan

This plan refines the acceptance criteria in `spec.md` against the entry points
in `contracts.md`. Example identifiers and clinical values are test fixtures,
not clinical rules. The strings `priority-a` and `priority-b` are deliberately
opaque because the spec does not define priority levels or their order.

## Acceptance-criterion cases

| ID | Requirement | Cases | Inside/outside | Control |
| --- | --- | --- | --- | --- |
| **AC-001** | FR-001 - Record a Triage Assessment | **TP-AC-001-01:** `POST /api/v1/encounters/E-1001/assessments` with `nurse_id: N-001` and `assessment: {symptoms: [{name: "chest pain"}], vital_signs: [{type: "heart_rate", value: 110, unit: "bpm"}], observations: ["alert"]}`. Expect `201`; body has nonempty `assessment_id`, `encounter_id: E-1001`, `status: stored`; one assessment is created for E-1001 and is retrievable for recommendation/clinical review. | No field-count or value limits are specified. **Extra boundary probe:** the minimum required assessment is undefined, so empty-vs-one-field expected behavior cannot be derived. | Same request with the listed nonempty assessment is the accepted control for future invalid-assessment cases. |
| **AC-002** | FR-002 and FR-007 - Display an advisory UrgencyRecommendation | **TP-AC-002-01:** With stored `A-1001`, `POST /api/v1/encounters/E-1001/urgency-recommendations` using `assessment_id: A-1001`; simulated provider returns `suggested_priority: priority-a`. Expect `201`; `recommendation_id` nonempty, `encounter_id: E-1001`, `assessment_id: A-1001`, `suggested_priority: priority-a`, `advisory: true`. Then `GET .../latest` expects `200` and the same recommendation. Side effects: recommendation created; no `TriagePriority` created. | No recommendation-score or priority boundary is defined. **Outside state:** unknown assessment should return contract `404` and create no recommendation, but the spec does not define the error body. | Stored A-1001 with the same provider output is the accepted control for unknown-assessment rejection. |
| **AC-003** | FR-003 - View the Recommendation Explanation | **TP-AC-003-01:** `GET /api/v1/encounters/E-1001/urgency-recommendations/R-1001/explanation`. Expect `200`; `recommendation_id: R-1001`, `factors: ["heart_rate=110 bpm", "symptom=chest pain"]`, `warnings: ["prototype decision support"]`, and `uncertainty` field present. No records are changed. | No factor-count or uncertainty format is specified. **Outside state:** unknown R-9999 should return contract `404` and create/update nothing. | Existing R-1001 request of the same shape is accepted. |
| **AC-004A** | FR-004 - Confirm the Recommended Priority | **TP-AC-004A-01:** `PUT /api/v1/encounters/E-1001/triage-priority` with `physician_id: P-001`, `recommended_priority: priority-a`, `selected_priority: priority-a`, `override_reason: null`. Expect `200`; `encounter_id: E-1001`, `triage_priority: priority-a`, `override_reason: null`, `queue_updated: true`. Side effects: one approved priority saved and queue reflects it. | No priority scale is defined. The meaningful boundary is equality: selected equals recommended (confirmation) versus differs (override). | This confirmation request is the accepted control for an override missing a reason. |
| **AC-004B** | FR-004 - Override the Recommended Priority | **TP-AC-004B-01:** Same endpoint with `recommended_priority: priority-a`, `selected_priority: priority-b`, `override_reason: "clinical assessment indicates different urgency"`. Expect `200`; `triage_priority: priority-b`, exact reason, `queue_updated: true`. Side effects: clinician-selected priority and reason saved; queue updated. | **Inside:** a nonempty reason. **Outside:** omitted/empty reason is AC-004C. Whether whitespace-only counts as empty is unspecified. | Same override with the quoted nonempty reason is accepted. |
| **AC-004C** | FR-004 - Reject an Override Without a Reason | **TP-AC-004C-01:** Same override as AC-004B but omit `override_reason`. Expect `422`; body `error: override_reason_required` and a nonempty `message`. Side effects: no priority decision created or changed; queue unchanged. **TP-AC-004C-02 control:** repeat with `override_reason: "clinical assessment indicates different urgency"`; expect `200` and the AC-004B side effects. | **Just inside:** one non-whitespace character (expected accepted by the proposed contract). **Just outside:** missing or empty string (expected `422`). Whitespace normalization is a spec gap. | TP-AC-004C-02 differs only by the required reason and must be accepted. |
| **AC-005** | FR-005 - Reassess a Waiting Patient | **TP-AC-005-01:** Given E-1001 is waiting with approved `priority-a`, `POST /api/v1/encounters/E-1001/reassessments` with `nurse_id: N-001` and `assessment: {symptoms: [{name: "chest pain", changed: true}], vital_signs: [{type: "heart_rate", value: 125, unit: "bpm"}], observations: ["condition changed"]}`. Expect `201`; new `assessment_id`, `encounter_id: E-1001`, `status: stored`, `requires_priority_review: true`, `prior_priority_unchanged: true`. Side effects: reassessment created and available for a new recommendation; approved priority remains `priority-a`. | No change threshold is defined. **Outside state:** encounter not in queue should return contract `409` and create nothing, but exact state rules are unspecified. | Waiting E-1001 with the same reassessment is accepted. |
| **AC-006** | FR-006 - Review an Advisory Routing Recommendation | **TP-AC-006-01:** With stored RR-1001, `GET /api/v1/encounters/E-1001/routing-recommendations/latest`. Expect `200`; `routing_recommendation_id: RR-1001`, `encounter_id: E-1001`, `advisory: true`, `automatic_transfer: false`, and `considered_inputs` present. No transfer record is created. | No facility-count or freshness limit exists. Unknown recommendation should return contract `404` and create nothing. | Existing RR-1001 request is accepted. |
| **AC-007** | FR-007 - Preserve Human Clinical Authority | **TP-AC-007-01:** Generate a recommendation for A-1001 as in AC-002. Expect `201`, `advisory: true`, `suggested_priority: priority-a`; verify no approved `TriagePriority` exists for E-1001 and queue is not changed by recommendation generation. | No confidence or priority limit is defined. Test both a provider result with `priority-a` and any other opaque priority token; neither may be approved automatically. | A later physician confirmation request from AC-004A is the accepted action that may create the priority. |
| **AC-008** | FR-008 - Use Urgency, Capacity, and Travel Time | **TP-AC-008-01:** `POST /api/v1/encounters/E-1001/routing-recommendations` with `administrator_id: ADM-001`, facilities `[{facility_id: F-1, capacity_status: {available_spaces: 2, estimated_wait_minutes: 20}}, {facility_id: F-2, capacity_status: {available_spaces: 1, estimated_wait_minutes: 10}}]`, travel times `{F-1: 12, F-2: 8}`, and stored clinician-approved `priority-a`. Expect `201`; nonempty `routing_recommendation_id`, `encounter_id: E-1001`, `advisory: true`, `automatic_transfer: false`; `considered_inputs` contains exact priority, both capacity records, and both travel times. No transfer/redirection side effect. The selected facility cannot be asserted because ranking is unspecified. | **Inside:** every facility has capacity and travel time. **Outside:** omit F-2 travel time; proposed contract says `422` and no recommendation, but the spec leaves missing-input behavior unresolved. | Restore `{F-1: 12, F-2: 8}` with otherwise identical input; accepted. |
| **AC-009** | FR-007 - Continue Triage When ML Is Unavailable | **TP-AC-009-01:** With A-1001 already stored, configure the injected provider as unavailable and `POST .../urgency-recommendations`. Expect `503`; body `error: ml_unavailable`, nonempty `message`; A-1001 remains stored; no recommendation or priority is created. Staff can still access the assessment. **TP-AC-009-02 control:** same request with an available provider; expect `201` advisory recommendation. | **Inside:** provider available. **Outside:** provider unavailable. No timeout duration is specified. How a physician records priority without a recommendation remains a spec gap. | TP-AC-009-02 has the same request and stored assessment; only provider availability changes. |

## Gap-checklist extras

These probes are required by the checklist. Rows marked **unresolved** cannot be
made executable without changing the specification.

| Extra ID | Category and requirement | Case | Expected result / control |
| --- | --- | --- | --- |
| EXTRA-FR-001-IDENTITY | Identity; FR-001 | Submit the AC-001 payload as actor role `EmergencyPhysician` rather than `TriageNurse`. | Proposed contract: `403`, no assessment created. Control: identical payload as `TriageNurse` is accepted. Authentication mechanism and trusted role source are unresolved. |
| EXTRA-FR-004-IDENTITY | Identity; FR-004 | Submit AC-004A as `TriageNurse`. | Proposed contract: `403`, no priority/queue change. Control: identical request as `EmergencyPhysician`. |
| EXTRA-FR-001-TYPES | Input types; FR-001 | Send `vital_signs: "110"` instead of a collection of structured values. | **Unresolved:** required schema and validation status are not in the spec. Control is AC-001's structured value. |
| EXTRA-FR-005-CONCURRENCY | Concurrency; FR-005 | Two nurses submit reassessments for E-1001 based on the same prior state. | **Unresolved:** conflict/version behavior is explicitly missing from architecture.md. |
| EXTRA-FR-004-CONCURRENCY | Concurrency; FR-004 | Two physicians save different priority decisions for E-1001 concurrently. | **Unresolved:** winner/conflict behavior is not specified. |
| EXTRA-FR-008-TIME | Time/freshness; FR-008 | Capacity information is old but otherwise complete. | **Unresolved:** no timestamp or freshness limit exists. Control is current complete input. |
| EXTRA-FR-004-PRECEDENCE | Error precedence; FR-004 | Unauthorized actor also omits the override reason. | **Unresolved:** authorization-versus-validation precedence is not specified. Single-error controls are EXTRA-FR-004-IDENTITY and AC-004C. |
| EXTRA-FR-005-LISTING | Listing; FR-005 | `GET /api/v1/patient-queue` with two encounters having different approved priority tokens. | **Unresolved:** priority levels/order and tie-breaking are not specified. Response must contain only waiting encounters, but exact order cannot be computed. |
| EXTRA-FR-002-RETURN | What is returned; FR-002 | Retrieve latest recommendation after two recommendations exist for the encounter. | **Unresolved:** “latest” selection needs timestamps/version ordering, which the spec does not define. |
| EXTRA-FR-008-MISSING | State/input availability; FR-008 | Request routing without approved priority, without capacity, or without travel time, one missing condition per case. | Proposed contract: one `409` for missing approved priority and separate `422` cases for missing inputs, with no recommendation created. Exact spec behavior remains unresolved. Controls restore exactly the missing value. |

## Spec gaps

### Requirements and criteria traceability

- Every FR-001 through FR-008 has at least one acceptance criterion in the
  traceability table.
- Every AC-001 through AC-009 names or traces to at least one functional
  requirement; there is no wholly orphaned acceptance criterion.
- FR-005's **queue viewing and ordering** behavior has no direct acceptance
  criterion. AC-005 tests reassessment, but not a queue listing result.
- FR-006 says staff review capacity and routing information, but AC-006 does not
  say which input fields must be returned. `architecture.md` attributes that to
  AC-010, which does not exist in `spec.md`.

### Cross-document identifier gaps

- `architecture.md` cites AC-010, but `spec.md` ends at AC-009.
- `architecture.md` cites NFR-001 through NFR-007, but `spec.md` has no NFR
  section or those identifiers.
- `architecture.md` uses AC-007 for reassessment, while `spec.md` AC-007 is the
  human-authority scenario. Reassessment is AC-005 in `spec.md`.
- `architecture.md` uses AC-009 for “no automatic priority before clinician
  decision,” while `spec.md` AC-009 is the ML-unavailable scenario.

### Behavioral gaps that prevent exact expected values

- Available `TriagePriority` values, ordering, and queue tie-breaking.
- Required assessment fields, field schemas, and validation behavior.
- Recommendation model outputs, explanation/uncertainty format, and mapping to
  a suggested priority.
- Routing ranking, missing/stale capacity or travel-time behavior, and the exact
  selected facility for the AC-008 fixture.
- Authentication, encounter identifier format, and trusted role source.
- Concurrent update and conflict rules.
- Error precedence and persistence-recovery behavior.
- Whether whitespace-only override reasons are valid.
- How a clinician records a priority when no recommendation is available.
- How (or whether) a reviewed human routing decision is recorded.

These gaps are intentionally not resolved in this test plan.
