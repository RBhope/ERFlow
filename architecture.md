# Overview

ERFlow is a proposed decision-support application for emergency department triage and patient flow. The architecture divides the application into modules for user interaction, access control, assessments, urgency recommendations, clinical priority and queue management, routing, and data storage.

# Modules

The following modules are logical parts of one application. They are not separate deployed services. Each module has one primary responsibility, and the requirements in the Responsibility column show why the module is needed.

| Module | Responsibility | May depend on |
| --- | --- | --- |
| User Interface | Present information and collect user actions for the triage and routing workflows. Needed by FR-001–FR-006 and NFR-005. | Access Control, Assessment, Recommendation, Priority and Queue, Routing |
| Access Control | Check whether a modeled user is authorized to perform a requested action. Needed by NFR-002. | Data Store |
| Assessment | Manage encounter assessments and reassessments. Needed by FR-001, FR-005, AC-001, and AC-007. | Data Store |
| Recommendation | Generate an advisory urgency recommendation and its explanation from assessment information. Needed by FR-002, FR-003, FR-007, AC-007, and NFR-005. | Assessment, Data Store |
| Priority and Queue | Manage clinician-selected priorities and the ordered waiting-patient view. Needed by FR-004, FR-005, AC-004, AC-005, and AC-006. | Data Store |
| Routing | Generate an advisory facility recommendation from the required routing inputs. Needed by FR-006, FR-008, AC-008, and AC-010. | Priority and Queue, Data Store |
| Data Store | Save and retrieve prototype records. Needed by AC-001, AC-004, AC-005, AC-007, and NFR-003. | None |

Access Control checks authorization before any role-specific operation is performed. The other modules must not rely only on a hidden or disabled user-interface control to enforce access.

# Request Flow

## Initial assessment and clinical priority

This is the main flow, from assessment entry to a clinician-selected priority.

1. The Triage Nurse submits an assessment through the User Interface. Access Control checks that the user is authorized to enter it (FR-001; NFR-002).

2. The Assessment module links the assessment to the selected PatientEncounter and saves it through the Data Store. If the assessment cannot be saved, the User Interface reports a save failure (AC-001; NFR-003).

3. Once the assessment is saved, the Recommendation module processes the available information. It returns an advisory urgency recommendation and its main contributing factors for display (FR-002, FR-003, FR-007; AC-002, AC-003; NFR-005).

4. If recommendation generation fails, the User Interface displays an error. The saved assessment remains available, and no final priority is assigned because of the failure (NFR-004).

5. The Emergency Physician opens the encounter. Access Control checks the user's role, and the User Interface displays the available assessment, recommendation, and explanation (FR-004; NFR-002).

6. The physician either confirms the recommended priority or overrides it. For an override, the physician must give a reason. The Priority and Queue module saves the decision against the encounter and updates the waiting-patient view (AC-004, AC-005; NFR-003).

7. The system does not assign the recommendation as the final priority before the clinician decides (FR-007; AC-009; NFR-001).

## Reassessment

1. The Triage Nurse selects a waiting encounter and submits updated assessment information. Access Control checks the user's role (FR-005; NFR-002).

2. The Assessment module saves the updated information for the same PatientEncounter (AC-007; NFR-003).

3. The Recommendation module processes the updated assessment and provides a new advisory recommendation for clinical review. The current TriagePriority is not changed automatically (AC-007; NFR-001).

4. If recommendation generation fails, the system displays an error and keeps the saved reassessment. It does not change the current priority automatically (NFR-004).

## Capacity-aware routing

1. The ER Administrator requests a routing review for an encounter. Access Control checks the user's role (FR-006; NFR-002).

2. The Routing module gets the clinically assigned triage priority, the available facility capacity, and the travel-time information (FR-008; AC-010).

3. The Routing module generates an advisory facility recommendation. The User Interface displays the recommended facility along with the priority, capacity, and travel-time inputs used in the review (AC-008, AC-010; NFR-001).

4. A human reviews the recommendation. The system does not start a patient transfer automatically (AC-008).

# Design Decisions

These decisions describe the proposed course prototype. Preferences are marked as such and can be revisited with the project team.

| Decision | Reason |
| --- | --- |
| Organize ERFlow as one application with logical modules. | **Preference:** FR-001–FR-008 need coordinated functionality but do not require independently deployed services. One application keeps the prototype manageable. |
| Use Python, Django, Django templates, and SQLite as a proposed stack. Consider scikit-learn for the ML component. | **Preference:** The specification does not prescribe a language, framework, database, or ML library. These are proposed choices that the team still needs to agree on. FR-007 still requires an ML model, and the model and data are yet to be selected. |
| Use synthetic patient data for the prototype and sample capacity and travel-time inputs for routing. | NFR-002 requires synthetic patient data. FR-006 and FR-008 require capacity and travel-time information but do not require live external integrations. Using sample routing inputs is a prototype preference. |
| Enforce role-specific access before each protected action. | NFR-002 requires role restrictions. The Domain Model and FR-001, FR-004, FR-005, and FR-006 identify the relevant roles and workflows. |
| Keep recommendation generation separate from the clinician's priority decision. | FR-004, FR-007, AC-007, AC-009, and NFR-001 require clinical control over the final priority. NFR-007 also calls for a separable recommendation function. |
| Allow a simulated recommendation provider to be substituted for testing. | NFR-007 requires a substitutable provider for testing. A simulated provider alone does not meet FR-007's ML-model requirement. |
| Save an assessment or reassessment before requesting a recommendation. | AC-001 and AC-007 require assessment information to be saved. NFR-004 requires a successfully submitted assessment to remain available if recommendation generation fails. |
| Link assessments and clinical decisions to the same encounter record. | NFR-003 requires saved assessments and priorities to stay linked to the correct PatientEncounter. AC-005 also requires an override reason. |
| After a reassessment, generate an updated advisory recommendation and keep the current clinical priority. | AC-007 requires an updated recommendation and states that the current priority is not changed automatically. |
| Use the available triage priority, capacity, and travel-time values as routing inputs and display them with the result. | FR-008 and AC-010 specify the routing inputs and their display. AC-008 requires the recommendation to stay advisory. |
| Report recommendation failures without discarding a successfully saved assessment. | NFR-004 specifies the error and retention behavior for both initial assessment and reassessment. |

# Constraints and Known Limits

## Current constraints and proposed technologies

- The prototype uses **synthetic patient data only** (NFR-002).
- The system keeps **human authority over the final triage priority**, and recommendations are advisory (FR-007; NFR-001).
- A recommendation failure must not discard a successfully submitted assessment. It must also not assign or change a priority automatically (NFR-004).
- The proposed stack is **Python, Django, Django templates, and SQLite**, with **scikit-learn** as a candidate for the ML component. These are preferences, not agreed team constraints. Hosting and other implementation choices are still to be decided.

## Known limits and future growth

- **ML model:** The specification requires an ML-assisted urgency recommendation. The model, training data, and evaluation approach are not yet selected. A simulated provider supports workflow testing, but it does not meet FR-007 on its own.
- **Prototype performance:** NFR-006 sets a proposed test target for a simulated provider. It does not show how a deployed ML model would perform.
- **External information:** The prototype does not assume live EHR, facility-capacity, or travel-time integrations. Adding them would need defined interfaces, current data sources, security controls, and integration testing.
- **Concurrent use:** The current specification does not say how to handle simultaneous updates to an encounter or conflicting priority decisions. Supporting multiple users reliably would need agreed concurrency rules, along with implementation and tests.
- **Clinical use:** This architecture describes a course prototype. It does not establish clinical validity, regulatory compliance, or suitability for patient care. Those claims would need further validation and review.

# Out of Scope

As stated in the specification's Description, ERFlow does not cover:

- Diagnosis.
- Treatment planning.
- Prescriptions.
- Billing.
- Complete hospital management.

# Spec Issues

The following points are still open in `spec.md`. They should be resolved or refined before the related behavior is implemented:

1. **Priority levels and ordering:** The specification does not define the available urgency or triage-priority levels, their order, or how a recommendation maps to a clinician-selected priority. The queue and confirmation workflow need these definitions.

2. **ML model and explanation:** The model, training data, evaluation approach, and method for identifying the patient factors shown in an explanation are not specified.

3. **Incomplete assessments:** The specification does not say which assessment fields are required. It also does not say how the system should respond when information needed for a recommendation is missing.

4. **Routing method and input availability:** FR-008 names the routing inputs. The facility-ranking method, and what happens when capacity or travel-time information is missing or outdated, are still undefined.

5. **Priority decision after recommendation failure:** NFR-004 requires the assessment to be kept and an error to be displayed. The specification does not say whether or how a clinician can enter a priority in ERFlow when no recommendation is available.

6. **Identity and concurrent changes:** The specification does not define the authentication mechanism, the encounter identifier format, or how to handle simultaneous edits and conflicting priority updates.

7. **Storage errors:** NFR-004 covers recommendation failure after an assessment is successfully submitted. The specification does not fully define recovery when an assessment or priority decision cannot be saved.

8. **Human routing decision:** The Description requires a human decision for routing, and AC-008 prevents automatic transfer. The specification does not say whether or how that decision is recorded in ERFlow.
