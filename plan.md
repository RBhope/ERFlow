# ERFlow Implementation Plan

## Starting point

This plan is based on `spec.md`, `architecture.md`, `contracts.md`, `test_plan.md`, the code skeleton, and the tests on `romina-spec`.

The original test suite had three failing tests. After Slice 1, the assessment test passes. The recommendation and priority tests still fail because their functions have not yet been implemented.

The existing tests cover parts of AC-001, AC-003, and AC-005. The remaining criteria do not have dedicated executable tests. A slice is complete when its listed tests pass, no previously passing test fails, and its listed behaviors are independently verified. A slice with no existing tests is not automatically complete.

## Slice 1 — Record a patient assessment

**Goal:** Allow a nurse to submit and save an assessment through one API route.

**Spec sources:** FR-001; AC-001; NFR-002, NFR-003; initial assessment flow in `architecture.md`.

**Criteria:** AC-001.

**Test that should turn green:** `test_T_001_record_assessment`.

**Skeleton to fill in:** `access_control.authorize`, `assessment.save_assessment`, and the necessary Data Store operations `get_role`, `get_records`, and `save_record`; `user_interface.save_assessment` and `POST /api/encounters/{encounter_id}/assessments`.

**Depends on:** None.

**Done when:** The listed test passes, a synthetic assessment can be saved through the route with the contract response, and no previously passing test fails. The existing test calls the module directly, so the route also needs an independent check.

**Verification:** The listed test passes. A route check returned 201 and confirmed that the assessment was saved for the selected encounter. Checks for an unknown user and an unknown encounter returned 403 and 404, respectively, without creating an assessment.

**Status:** Completed.

## Slice 2 — View a saved recommendation

**Goal:** Retrieve and display a saved advisory recommendation and its factors for an encounter.

**Spec sources:** FR-003; AC-003; NFR-005.

**Criteria:** AC-003, partially verified using a synthetic recommendation. Model-generated explanations remain future work.

**Test that should turn green:** `test_T_003_view_explanation`.

**Skeleton to fill in:** `recommendation.get_recommendation`, `user_interface.get_recommendation`, and `GET /api/encounters/{encounter_id}/recommendation`.

**Depends on:** Slice 1 for storage and encounter foundations.

**Done when:** The listed test passes, the route returns a saved synthetic recommendation with its advisory status and factors, and no previously passing test fails.

**Status:** Completed for synthetic recommendation retrieval.

## Slice 3 — Confirm or override a priority

**Goal:** Allow an authorized physician to confirm a recommendation or override it with a reason.

**Spec sources:** FR-004; AC-004, AC-005; NFR-001, NFR-002, NFR-003.

**Criteria:** AC-004, AC-005.

**Test that should turn green:** `test_T_005_override_priority`.

**Skeleton to fill in:** `priority_queue.record_priority`, `user_interface.record_priority`, and `POST /api/encounters/{encounter_id}/priority`.

**Depends on:** Slices 1 and 2.

**Done when:** The listed test passes, independent checks cover confirmation, override reason, and queue update, and no previously passing test fails. Confirmation and override should be reviewed separately because the override adds a reason.

**Status:** Not started.

## Slice 4 — Generate recommendations and support reassessment

**Goal:** Generate an advisory recommendation, show the waiting queue, and support reassessment without automatically changing the clinical priority.

**Spec sources:** FR-002, FR-005, FR-007; AC-002, AC-006, AC-007, AC-009; NFR-001, NFR-004, NFR-007.

**Criteria:** AC-002, AC-006, AC-007, AC-009.

**Tests that should turn green:** None currently in the suite for these criteria.

**Skeleton to fill in:** `recommendation.generate_recommendation`, `user_interface.generate_recommendation`, and `POST /api/encounters/{encounter_id}/recommendations`; `priority_queue.get_queue`, `user_interface.get_queue`, and `GET /api/queue`; `assessment.get_assessment`, `user_interface.get_assessment`, and `GET /api/encounters/{encounter_id}/assessment`; reassessment behavior in the existing assessment and recommendation functions and routes.

**Depends on:** Slices 1–3.

**Done when:** The full suite has no regressions and independent checks cover recommendation generation, the queue, saved reassessment, an updated recommendation, and unchanged clinical priority. The ML model and priority ordering must first be defined. A simulated provider can test the workflow but does not by itself fulfill FR-007.

**Status:** Not started.

## Slice 5 — Review capacity and routing

**Goal:** Show facility capacity and an advisory routing recommendation with its inputs, without initiating a transfer.

**Spec sources:** FR-006, FR-008; AC-008, AC-010.

**Criteria:** AC-008, AC-010.

**Tests that should turn green:** None currently in the suite for these criteria.

**Skeleton to fill in:** `data_store.get_facilities`, `routing.get_capacity`, `routing.review_routing`, `user_interface.get_capacity`, and `user_interface.review_routing`; `GET /api/facilities/capacity` and `POST /api/encounters/{encounter_id}/routing`.

**Depends on:** Slices 1, 3, and 4.

**Done when:** The full suite has no regressions and independent checks cover capacity, the advisory result, its inputs, and no automatic transfer. The routing rule must first be defined.

**Status:** Not started.

## Unassigned items

- **Acceptance criteria:** None.
- **Failing tests:** None unassigned. The two remaining failing tests are assigned to Slices 2 and 3.
- **Contract functions and routes:** None.

## Design questions

Slice 1 uses SQLite with synthetic starter data. The record structure and local setup are documented in `contracts.md`. The `X-User-Id` header is a prototype testing convention; secure authentication remains open.

Later slices need decisions about the ML model and explanation, priority ordering, routing rules, reassessment, and errors. The current documents do not define all of these details.

## Test issues

- `test_T_001_record_assessment` does not verify the encounter association required by AC-001. Slice 1's route and storage were checked separately.
- `test_T_005_override_priority` does not verify the queue update required by AC-005.
- The assessment test uses a mock store and does not explicitly set up an existing encounter. The SQLite route check used a synthetic encounter.

**Next action:** Begin Slice 2 and make `test_T_003_view_explanation` pass.
