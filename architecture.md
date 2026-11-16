# Overview

ERFlow is a proposed decision-support application for emergency department triage and patient flow. It is organized as one application with modules for user interaction, access control, assessments, recommendations, clinical priority and queue management, routing, and data storage.

# Modules

These modules are logical parts of one application, not separate deployed services.

| Module             | Responsibility                                                                                                             | May depend on                                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| User Interface     | Collect user actions and present information for triage and routing workflows. Supports FR-001–FR-006 and NFR-005.         | Access Control, Assessment, Recommendation, Priority and Queue, Routing |
| Access Control     | Check whether a modeled user is authorized to perform an action. Supports NFR-002.                                         | Data Store                                                              |
| Assessment         | Manage encounter assessments and reassessments. Supports FR-001, FR-005, AC-001, and AC-007.                               | Access Control, Data Store                                              |
| Recommendation     | Generate advisory urgency recommendations and explanations. Supports FR-002, FR-003, FR-007, AC-007, and NFR-005.          | Assessment, Data Store                                                  |
| Priority and Queue | Manage clinician-selected priorities and the waiting-patient view. Supports FR-004, FR-005, and AC-004–AC-006.             | Access Control, Data Store                                              |
| Routing            | Generate advisory facility recommendations using the required routing inputs. Supports FR-006, FR-008, AC-008, and AC-010. | Priority and Queue, Data Store                                          |
| Data Store         | Save and retrieve prototype records. Supports AC-001, AC-004, AC-005, AC-007, and NFR-003.                                 | None                                                                    |

Access Control checks authorization before role-specific actions. The application must not rely only on hiding or disabling a user-interface control to restrict access.

# Request Flow

## Initial assessment and clinical priority

1. A Triage Nurse submits assessment information through the User Interface. Access Control checks the nurse's role (FR-001; NFR-002).
2. The Assessment module links the assessment to the selected PatientEncounter and saves it through the Data Store. The User Interface reports a save failure (AC-001; NFR-003).
3. The Recommendation module processes the available assessment information and returns an advisory urgency recommendation and its main contributing factors for display (FR-002, FR-003, FR-007; AC-002, AC-003).
4. If recommendation generation fails, the User Interface displays an error. The saved assessment remains available, and no final priority is assigned because of the failure (NFR-004).
5. An Emergency Physician reviews the encounter and recommendation. Access Control checks the physician's role.
6. The physician confirms or overrides the recommendation. An override includes a reason. The Priority and Queue module saves the decision for the encounter and updates the queue (FR-004; AC-004, AC-005).
7. The system does not assign the recommendation as the final priority before the clinician decides (FR-007; AC-009; NFR-001).

## Reassessment

1. A Triage Nurse submits updated assessment information for a waiting encounter. Access Control checks the nurse's role (FR-005; NFR-002).
2. The Assessment module saves the updated information for the same encounter (AC-007; NFR-003).
3. The Recommendation module provides an updated advisory recommendation for clinical review. The current clinical priority is not changed automatically (AC-007; NFR-001).
4. If recommendation generation fails, the application displays an error and retains the saved reassessment without automatically changing the current priority (NFR-004).

## Capacity-aware routing

1. An ER Administrator requests a routing review. Access Control checks the user's role (FR-006; NFR-002).
2. The Routing module obtains the clinically assigned priority, facility capacity, and travel-time information (FR-008; AC-010).
3. The User Interface displays the advisory facility recommendation and the inputs used (AC-008, AC-010).
4. A human reviews the recommendation. The system does not automatically initiate a transfer (AC-008).

# Design Decisions

| Decision                                                                                                          | Reason                                                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Organize ERFlow as one application with logical modules.                                                          | The requirements need coordinated functions but do not require separately deployed services.                                                  |
| Use Python, Django, and SQLite for this prototype. Django templates are a proposed option for the user interface. | This stack supports a manageable course prototype. The team may revisit these choices.                                                        |
| Consider scikit-learn for the ML component.                                                                       | The specification requires ML-assisted recommendations, but the model and data have not been selected.                                        |
| Use synthetic patient data and sample capacity and travel-time inputs.                                            | NFR-002 requires synthetic patient data. The routing requirements do not require live integrations.                                           |
| Check role-specific access before protected actions.                                                              | NFR-002 restricts actions to their modeled roles.                                                                                             |
| Keep recommendations separate from clinical priority decisions.                                                   | FR-007 and NFR-001 preserve clinical authority. NFR-007 requires a separable recommendation function.                                         |
| Allow a simulated recommendation provider for testing.                                                            | NFR-007 requires a substitutable provider. A simulation alone does not satisfy the ML requirement in FR-007.                                  |
| Save assessments before requesting recommendations.                                                               | AC-001 and AC-007 require assessments to be saved. NFR-004 requires a successful save to remain available if recommendation generation fails. |
| Associate assessments and clinical decisions with the encounter.                                                  | NFR-003 requires saved records to remain linked to the correct encounter.                                                                     |
| Display the priority, capacity, and travel-time inputs used for routing.                                          | FR-008 and AC-010 identify these inputs.                                                                                                      |

# Constraints and Known Limits

- The prototype uses **synthetic patient data only** (NFR-002).
- Urgency and routing recommendations are advisory. An authorized clinician retains control of the final triage priority (FR-007; NFR-001).
- A recommendation failure must not discard a successfully saved assessment or automatically assign or change a priority (NFR-004).
- The ML model, training data, and evaluation approach have not been selected. A simulated provider is for testing and does not fulfill FR-007 by itself.
- The performance target in NFR-006 applies to a simulated provider and does not establish the performance of a deployed ML model.
- The prototype does not assume live EHR, facility-capacity, or travel-time integrations.
- This course prototype has not been validated for clinical use.

# Out of Scope

ERFlow does not cover diagnosis, treatment planning, prescriptions, billing, or complete hospital management.

# Spec Issues

The following points remain open in `spec.md` and should be resolved before implementing the related behavior:

1. **Priority levels and ordering:** The available levels, their order, and how recommendations map to clinical priorities are not defined.
2. **ML model and explanation:** The model, training data, evaluation approach, and method for identifying contributing factors are not specified.
3. **Incomplete assessments:** The required assessment fields and the response to information missing for a recommendation are not defined. For the initial assessment slice, available assessment fields can be saved without requiring additional clinical fields.
4. **Routing:** The facility-ranking method and the handling of missing or outdated capacity and travel-time inputs are not defined.
5. **Priority after recommendation failure:** The specification does not say whether or how a clinician can enter a priority when no recommendation is available.
6. **Identity and concurrent changes:** The authentication mechanism, encounter identifier format, and handling of simultaneous or conflicting updates are not defined.
7. **Storage errors:** Recovery after an assessment or priority cannot be saved is not fully defined.
8. **Human routing decision:** The specification requires a human routing decision but does not say whether or how it is recorded.
