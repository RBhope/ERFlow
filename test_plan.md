# ERFlow Test Plan

## Basis and conventions

This plan uses `spec.md` and `architecture.md` on the `romina-spec` branch. It contains no implementation-derived behavior. IDs T-001–T-010 refine AC-001–AC-010; X-IDs are extra cases. Blocked cases need an agreed rule before they can be tested. The test data is synthetic; the priority values are placeholders. `E1` and `E2` are distinct existing encounters; `A1` and `A2` are distinct assessments. `N1`, `P1`, and `R1` represent authorized nurse, physician, and administrator users. `U1` is an authenticated user with an incorrect role. A fake recommendation provider can return fixed outputs for workflow testing; it does not demonstrate an ML model or validate a clinical explanation.

Actions such as “submit” or “retrieve” are abstract calls: exact function names, routes, payload fields, HTTP statuses and error codes will be specified in `contracts.md`. The current specification does not set HTTP codes or response schemas, so this plan does not assert invented ones. “Accepted” and “rejected” describe the required outcomes. “No mutation” means compare all affected records to the pre-request state, including no newly created record and no changes to existing records; this is stronger than checking only creation.

## Acceptance-criterion scenarios

### T-001 — Record an assessment (AC-001; FR-001)

**Given** N1 has opened E1 and no assessment A1 exists for E1  
**When** N1 submits A1 with complaint `headache`, symptom `dizziness`, and heart rate `90 bpm`  
**Then** the action is accepted and retrieving E1 shows A1 associated with E1. The precise response fields and success status are to be defined in the contract. 

### T-002 — Review a recommendation (AC-002; FR-002)

**Given** A1 is available for E1 and a test provider is configured to return the advisory recommendation `TEST-PRIORITY-A`  
**When** the assessment is processed  
**Then** the action is accepted and the result displayed for E1 contains that advisory recommendation.  No automatic final priority is assigned (also tested in T-009).

### T-003 — View an explanation (AC-003; FR-003; NFR-005)

**Given** a test provider has produced E1's recommendation with `dizziness` as its main contributing factor  
**When** N1 reviews the recommendation  
**Then** the display includes the recommendation, its advisory status, and `dizziness` as a contributing factor. 

### T-004 — Confirm a priority (AC-004; FR-004; NFR-003)

**Given** E1 has advisory recommendation `TEST-PRIORITY-A` and P1 is reviewing it  
**When** P1 confirms the recommendation  
**Then** the action is accepted, E1's saved priority is `TEST-PRIORITY-A`, and the waiting view reflects the decision. Reopen E1 to check the association. The ordering among distinct priority levels is unspecified.

### T-005 — Override a priority (AC-005; FR-004; NFR-003)

**Given** E1 has advisory recommendation `TEST-PRIORITY-A` and P1 is reviewing it  
**When** P1 selects the distinct fixture value `TEST-PRIORITY-B` and records `Clinical assessment` as the reason  
**Then** the action is accepted, E1's saved priority is `TEST-PRIORITY-B`, its override reason is saved, and the waiting view reflects the decision. Reopen E1 to check the association and reason. The actual permitted priority values remain unspecified.

### T-006 — View the waiting queue (AC-006; FR-005)

**Given** E1 and E2 are waiting and both have clinician-assigned priority `TEST-PRIORITY-A`  
**When** N1 opens the queue  
**Then** the view includes E1 and E2 with their current priority. The allowed fixture priority value and the order between equal-priority encounters are unspecified, so this case requires agreed test data before execution. A test of ordering across distinct priorities is blocked until the priority order is defined.

### T-007 — Reassess a waiting patient (AC-007; FR-005; NFR-001)

**Given** E1 is waiting with clinician-assigned priority `TEST-PRIORITY-A`, and the test provider returns a new advisory recommendation `TEST-PRIORITY-B` for A2  
**When** N1 submits A2 with changed symptom `nausea`  
**Then** A2 is saved for E1, the new advisory recommendation is available for clinical review, and E1's current clinical priority remains `TEST-PRIORITY-A`. 

### T-008 — Review routing (AC-008; FR-006)

**Given** E1 has a clinician-assigned priority and test facility capacity and travel-time data are available  
**When** R1 requests a routing review  
**Then** an advisory routing recommendation associated with E1 is displayed and no transfer is automatically initiated. The facility selection algorithm and any transfer record representation are unspecified, so no exact selected facility is asserted here.

### T-009 — Preserve human authority (AC-009; FR-007; NFR-001)

**Given** E1 has no final priority and a recommendation has been generated  
**When** the recommendation is displayed  
**Then** no final priority is assigned to E1. Snapshot the encounter and verify no priority decision is created by display alone.

### T-010 — Display routing inputs (AC-010; FR-008)

**Given** E1 has clinical priority `TEST-PRIORITY-A`, and the only facility option `F1` has capacity `2 available spaces` and travel time `10 minutes`  
**When** R1 requests routing and the result recommends F1  
**Then** the display contains F1 and the priority, capacity, and travel-time values used. The facility selection rule is not yet defined.

## Extra cases and gap checklist

### X-001 — Role rejection and valid control (NFR-002; FR-001)

**Rejection:** Given E1 exists, U1 has the physician role, and A1 is otherwise valid, U1 attempts to submit A1 as an assessment. The action is rejected and assessment and encounter state remain unchanged, with no assessment created.  
**Control:** Change only the actor to N1, with the same E1 and A1. The action is accepted and A1 is associated with E1 (T-001). Exact rejection status and error code are contract decisions.

### X-002 — Role rejection and valid control (NFR-002; FR-004)

**Rejection:** Given an available recommendation on E1, N1 attempts to confirm it using the same otherwise valid request as P1. The action is rejected; the encounter, priority decisions, and queue remain unchanged, and no priority decision is created.  
**Control:** Change only the actor to P1; the same confirmation is accepted and recorded (T-004).

### X-003 — Role rejection and valid control (NFR-002; FR-006)

**Rejection:** Given the inputs required for E1's routing review, N1 requests routing with otherwise identical inputs to R1. The action is rejected; no routing recommendation or transfer is created and existing data is unchanged.  
**Control:** Change only the actor to R1; the review is accepted and an advisory result is displayed (T-008).

### X-004 — Role rejection and valid control (NFR-002; FR-005)

**Rejection:** Given E1 is waiting, P1 submits otherwise valid reassessment A2. The action is rejected; no reassessment or recommendation is created, and E1 and its priority remain unchanged.  
**Control:** Change only the actor to N1; the reassessment is accepted and processed (T-007).

### X-005 — Initial recommendation failure (NFR-004)

**Given** N1 submits A1 for E1 and the save succeeds  
**When** the injected recommendation provider fails  
**Then** an error is displayed, A1 remains saved for E1, and no final priority is assigned. The precise status and error code are unspecified. This tests a dependency failure after a successful assessment save, not rejection of that save.  
**Control:** With the same assessment and state, use a working provider; an advisory recommendation is displayed (T-002).

### X-006 — Reassessment recommendation failure (NFR-004)

**Given** E1 is waiting with priority `TEST-PRIORITY-A` and A2 is successfully saved  
**When** the provider fails on the new recommendation  
**Then** an error is displayed, A2 remains saved, and E1's priority remains `TEST-PRIORITY-A`.  
**Control:** With the same reassessment and state, use a working provider and verify T-007.

### X-007 — Correct encounter association (NFR-003)

**Given** E1 and E2 are distinct and A1 has been saved for E1  
**When** the records are reopened  
**Then** A1 is associated with E1 and not E2. Repeat with P1's priority decision and override reason for E1; they remain associated with E1 and not E2.

### X-008 — Response-time limit (NFR-006)

**Given** a locally available test dataset and simulated provider, run 100 sequential requests and time each from request to display of recommendation or error.  
**Time boundary:** Given 95 responses each take exactly `5.000` seconds and 5 take `5.001` seconds, the target is met: exactly 95 are at or below the limit. If one of the 95 changes from `5.000` to `5.001` seconds and all other durations stay the same, only 94 meet the limit and the target is not met.  
**Count boundary:** Compare exactly 95 qualifying responses with exactly 94, out of 100 sequential requests. These are evaluations of the performance target, not rejected requests. Record timing method, precision, and environment. These fixed-duration examples check the threshold calculation; an actual system performance assessment must measure real elapsed request-to-display times over 100 sequential requests.

### X-009 — Provider substitution (NFR-007)

**Given** the assessment, storage, and priority-handling functions are unchanged  
**When** the test provider is substituted for the recommendation provider  
**Then** assessment, recommendation, and clinician-priority workflows can be exercised through the documented contracts. This does not validate the ML requirement.

### X-010 — Queue ordering across distinct priorities (AC-006; FR-005) — blocked

**Given** waiting E1 and E2 have different clinician-assigned priorities  
**When** N1 opens the queue  
**Then** encounters appear in priority order. Exact expected order cannot be computed until the specification defines priority levels and their order.

### X-011 — Routing input effects (FR-008) — blocked

Vary one routing input at a time while keeping the other inputs fixed; assess whether the selected facility reflects the specified decision rule. FR-008 requires all three factors to be considered, but the specification does not define how they affect selection. Exact outputs cannot be computed yet.

### X-012 — Concurrent priority updates (FR-004; NFR-003) — blocked

**Given** P1 and another authorized physician review the same E1 and submit different priorities concurrently  
**When** both updates are processed  
**Then** the specification does not define which update wins, whether either request is rejected, or the final queue state. Document this as a gap; do not assert a chosen conflict policy.

### X-013 — Invalid assessment input type (FR-001) — blocked

**Given** a nurse submits an assessment where the heart rate is a nonnumeric string such as `"abc"`, with all other input held valid  
**When** the assessment is submitted  
**Then** the specification does not define field types, validation, rejection, or an error result. A valid numeric-input control and no-mutation assertions can be finalized if a validation rule is added; rejection cannot be assumed from the existing specification.

### X-014 — Storage failure (FR-001; FR-004; NFR-003) — blocked

**Given** a valid assessment or priority decision and a storage failure  
**When** a save is attempted  
**Then** the architecture expects the assessment save failure to be reported, but the specification does not define the response, recovery, or persistence semantics for failed saves. Do not assert that no partial record exists until atomicity rules are specified.

### X-016 — Unknown encounter identity (FR-001; NFR-003) — blocked

**Given** a nurse submits an otherwise valid assessment referring to an encounter that does not exist  
**When** it is submitted  
**Then** the specification does not state the response or whether the encounter can be created implicitly. Its status, error, side effects, and a matched valid control remain to be specified.

### X-017 — Empty waiting list (FR-005; AC-006) — blocked

**Given** no encounters are waiting  
**When** a nurse opens the patient queue  
**Then** the specification does not define the empty response or display; do not assume a particular message or response body.

### X-018 — Capacity freshness (FR-008) — blocked

**Given** two otherwise identical routing requests where one uses current capacity information and the other uses stale capacity information  
**When** routing is requested  
**Then** the specification does not define freshness limits, rejection, warning, or fallback. No exact result or rejection control can be asserted until a rule is agreed.

## Spec gaps and checklist

### Requirements without a dedicated acceptance criterion

Every functional requirement FR-001 through FR-008 is referenced by at least one criterion AC-001 through AC-010. NFR-001 through NFR-005 have related acceptance scenarios, but some of their added conditions require the extra checks above. NFR-006 (response-time target) and NFR-007 (provider substitution) have no dedicated AC; they are addressed in X-008 and X-009. The synthetic-only constraint in NFR-002 has no explicit verification mechanism: determining whether arbitrary data is genuinely synthetic is not specified.

### Acceptance criteria without a requirement

None found: AC-001–AC-010 each identify a functional requirement in `spec.md`.

### Additional unresolved points

Priority values and ordering (X-010); routing rules and stale data (X-011, X-018); concurrency (X-012); input types and ranges (X-013); storage errors (X-014); unknown encounters (X-016); and empty queue behavior (X-017) remain unspecified. The ML model, explanations, authentication, manual priority after failure, and recording a routing decision also need decisions. The specification does not define error precedence when more than one issue occurs. Rejection tests above each use one invalid condition. HTTP contracts must be proposed separately and should be marked as design choices, not treated as existing spec rules.
