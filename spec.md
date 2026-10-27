# Description

ERFlow is an ML-assisted decision-support system for emergency-department triage and capacity-aware patient flow. It helps healthcare professionals record and review patient assessment information, generate and explain an advisory urgency recommendation, establish and maintain a clinician-approved patient priority, reassess patients whose condition changes, and compare nearby emergency facilities using capacity and travel-time information. ERFlow does not diagnose patients, prescribe treatment, create treatment plans, perform billing, replace clinicians, assign a final triage priority autonomously, or transfer or redirect a patient autonomously. Authorized healthcare professionals retain final authority over all clinical and routing decisions. Complete hospital management is also outside the project scope.

# Goals

1. **G-001 - Assess patient urgency effectively.** The Triage Nurse should have sufficient patient assessment information and decision support to determine how urgently the patient needs attention.
2. **G-002 - Prioritize patients appropriately.** Waiting patients should be prioritized according to their current clinical urgency rather than arrival order alone.
3. **G-003 - Support safe and timely emergency-care decisions.** ERFlow should provide useful information and recommendations that help healthcare professionals make timely decisions without replacing professional judgment.
4. **G-004 - Make informed triage decisions.** The Emergency Physician should have access to the patient, assessment, recommendation, and priority information needed to review and make triage decisions.
5. **G-005 - Support appropriate patient routing and effective ER capacity management.** ERFlow should help authorized staff use facility capacity, patient urgency, estimated wait time, and travel information when making patient-flow and routing decisions.

# Domain Model

## Actors

- **Triage Nurse (`TriageNurse`)** - Records the initial and updated `TriageAssessment`, reviews the advisory `UrgencyRecommendation` and its explanation, and views the prioritized queue.
- **Emergency Physician (`EmergencyPhysician`)** - Reviews patient and triage information and confirms or overrides the recommended priority. The physician has final authority over the `TriagePriority` in this specification.
- **ER Administrator (`ERAdministrator`)** - Reviews or maintains facility capacity information and reviews advisory routing recommendations.
- **Patient** - The person receiving emergency care. A patient is associated with one or more emergency-care encounters over time but is not modeled as a direct ERFlow user in the MVP.
- **ERFlow System** - Stores and presents triage information, invokes the ML component, explains recommendations, maintains the patient queue, and generates advisory routing recommendations.
- **External information systems** - The EHR/patient-record system, ER capacity/bed-management system, and travel-time or EMS information source provide information to ERFlow. They do not make ERFlow's final clinical or routing decisions.

Only the Triage Nurse, Emergency Physician, and ER Administrator are user-story stakeholders in the MVP.

## Objects

- **`Person`** - General superclass for people represented in the domain.
- **`Patient`** - Person receiving emergency care.
- **`HealthcareProfessional`** - General superclass for authorized clinical and administrative roles.
- **`TriageNurse`**, **`EmergencyPhysician`**, **`ERAdministrator`** - Specialized healthcare-professional roles described above.
- **`PatientEncounter`** - One emergency-care visit connecting a patient to assessments, priority, queue, and routing information.
- **`TriageAssessment`** - Symptoms, vital signs, history, allergies, medications, observations, and other triage information recorded for a `PatientEncounter`.
- **`Symptom`** - A symptom reported or observed during an assessment.
- **`VitalSign`** - A measured value such as heart rate, blood pressure, oxygen saturation, or temperature.
- **`MedicalHistory`**, **`Allergy`**, **`Medication`**, **`ClinicalObservation`** - Supporting clinical information used in a `TriageAssessment`.
- **`UrgencyRecommendation`** - An advisory ML-generated estimate of patient urgency. It may suggest a priority but is not the final `TriagePriority`.
- **`RecommendationExplanation`** - The main patient factors, warnings, or available uncertainty information associated with an `UrgencyRecommendation`.
- **`TriagePriority`** - The clinician-confirmed or clinician-selected priority for a `PatientEncounter`.
- **`PatientQueue`** - The prioritized collection of waiting `PatientEncounter` records. Queue ordering uses the clinician-approved `TriagePriority`.
- **`ERFacility`** - A participating emergency facility that may be considered during routing review.
- **`CapacityStatus`** - Current facility information such as available treatment spaces, load, and estimated wait time.
- **`RoutingRecommendation`** - An advisory facility recommendation based on `TriagePriority`, `CapacityStatus`, and travel time.

### Key Relationships and Rules

- A `Patient` has a `PatientEncounter`.
- A `TriageAssessment` is for one `PatientEncounter`, is recorded by a `TriageNurse`, and may contain symptoms, vital signs, history, allergies, medications, and observations.
- A `TriageAssessment` may produce an `UrgencyRecommendation` with a `RecommendationExplanation` and a suggested priority.
- The suggested priority becomes the encounter's `TriagePriority` only after the `EmergencyPhysician` confirms it or selects another priority.
- A `PatientQueue` contains waiting `PatientEncounter` records and reflects their clinician-approved `TriagePriority` values.
- An `ERFacility` has a `CapacityStatus` maintained or reviewed by an `ERAdministrator`.
- A `RoutingRecommendation` uses the encounter's `TriagePriority`, facility `CapacityStatus`, and travel time, and is reviewed by an authorized human before any routing action.
- If the ML component is unavailable, healthcare staff must be able to continue the normal triage workflow without an ML recommendation.

# Functional Requirements

## User-Facing Requirements

### FR-001 - Record a Triage Assessment

As a **Triage Nurse**, I want to record a patient's symptoms, `VitalSign` values, and other `TriageAssessment` information, so that I can **assess patient urgency effectively**.

- Supports: G-001 and G-002.

### FR-002 - Review an ML-Assisted Urgency Recommendation

As a **Triage Nurse**, I want to review an ML-assisted `UrgencyRecommendation`, so that I can **prioritize patients appropriately**.

- Supports: G-001, G-002, and G-003.

### FR-003 - View the Recommendation Explanation

As a **Triage Nurse**, I want to see the main patient factors that influenced the `UrgencyRecommendation`, so that I can receive **understandable, human-centered decision support**.

- Supports: G-003.

### FR-004 - Confirm or Override the Recommended Priority

As an **Emergency Physician**, I want to confirm or override the recommended patient priority, so that I can **maintain clinical control**.

- Supports: G-004.
- When overriding the recommendation, the physician must record an override reason.

### FR-005 - View the Queue and Reassess a Waiting Patient

As a **Triage Nurse**, I want to view `PatientEncounter` records by their current `TriagePriority` and update the `TriageAssessment` when a patient's condition changes, so that I can **prioritize patients appropriately**.

- Supports: G-001 and G-002.
- A reassessment returns the encounter to recommendation and clinical-priority review; it does not autonomously replace the approved `TriagePriority`.

### FR-006 - Review Capacity and Routing Information

As an **ER Administrator**, I want to review `CapacityStatus` information and `RoutingRecommendation` results, so that I can **support appropriate capacity-aware patient routing**.

- Supports: G-005.
- The displayed routing result is advisory and does not initiate a patient transfer.

## System Requirements

### FR-007 - ML Processing and Human Authority

The system shall process the available `TriageAssessment` using the selected machine-learning model or models and generate an `UrgencyRecommendation`. The system shall clearly present the result as advisory and shall not automatically assign the encounter's `TriagePriority`. This preserves the quality of maintaining clinical control by requiring an authorized healthcare professional to confirm or override the recommendation.

- Supports: G-002, G-003, and G-004.

### FR-008 - Capacity-Aware Routing Logic

The system shall consider the clinician-approved `TriagePriority`, participating-facility `CapacityStatus`, and travel time when generating a `RoutingRecommendation`. The system shall present the result for authorized human review and shall not automatically transfer or redirect the patient.

- Supports: G-005.

# Acceptance Criteria

```gherkin
Feature: ERFlow triage and patient-flow decision support

  Scenario: AC-001 - Record a TriageAssessment for FR-001
    Given a TriageNurse has opened a PatientEncounter
    When the nurse enters the patient's triage information
    And submits the TriageAssessment
    Then ERFlow stores the TriageAssessment for that PatientEncounter
    And the assessment is available for urgency processing and clinical review

  Scenario: AC-002 - Display an advisory UrgencyRecommendation for FR-002
    Given a submitted TriageAssessment is available
    When ERFlow processes the available assessment information
    Then ERFlow displays an UrgencyRecommendation to the TriageNurse
    And the recommendation is identified as advisory
    And ERFlow does not assign a final TriagePriority

  Scenario: AC-003 - Explain the recommendation for FR-003
    Given an UrgencyRecommendation has been generated
    When the TriageNurse reviews the recommendation
    Then ERFlow displays the main patient factors that influenced it
    And ERFlow displays available warning or uncertainty information

  Scenario: AC-004A - Confirm the recommended priority for FR-004
    Given an EmergencyPhysician is reviewing a PatientEncounter
    And an UrgencyRecommendation is available
    When the physician confirms the suggested priority
    Then ERFlow saves the confirmed value as the TriagePriority
    And ERFlow updates the PatientQueue using that TriagePriority

  Scenario: AC-004B - Override the recommended priority for FR-004
    Given an EmergencyPhysician is reviewing a PatientEncounter
    And an UrgencyRecommendation is available
    When the physician selects another priority
    And records an override reason
    Then ERFlow saves the physician-selected value as the TriagePriority
    And ERFlow stores the override reason
    And ERFlow updates the PatientQueue using the physician-selected TriagePriority

  Scenario: AC-004C - Reject an override without a reason for FR-004
    Given an EmergencyPhysician is reviewing a PatientEncounter
    And an UrgencyRecommendation is available
    When the physician selects another priority
    But does not record an override reason
    Then ERFlow does not save the overridden TriagePriority
    And ERFlow identifies the missing override reason

  Scenario: AC-005 - Reassess a waiting patient for FR-005
    Given a PatientEncounter is in the PatientQueue
    And the patient's condition has changed
    When the TriageNurse records changed symptoms, VitalSign values, or observations
    And submits the updated TriageAssessment
    Then ERFlow stores the updated assessment for the PatientEncounter
    And ERFlow makes the updated information available for a new urgency recommendation
    And the encounter requires clinical-priority review before its approved TriagePriority changes

  Scenario: AC-006 - Review an advisory routing recommendation for FR-006
    Given CapacityStatus information is available for participating ERFacility options
    And the PatientEncounter has a clinician-approved TriagePriority
    When the ERAdministrator requests a routing review
    Then ERFlow displays a RoutingRecommendation
    And the recommendation is identified as advisory
    And ERFlow does not initiate a patient transfer

  Scenario: AC-007 - Preserve human clinical authority for FR-007
    Given ERFlow has generated an UrgencyRecommendation
    When the recommendation is displayed
    Then the PatientEncounter remains without a new approved TriagePriority
    And no new TriagePriority is saved unless an EmergencyPhysician confirms the recommendation or selects another priority

  Scenario: AC-008 - Use urgency, capacity, and travel time for FR-008
    Given a clinician-approved TriagePriority is available
    And current CapacityStatus information is available for participating ERFacility options
    And travel-time information is available for those facilities
    When ERFlow generates a RoutingRecommendation
    Then the recommendation considers TriagePriority, CapacityStatus, and travel time
    And the recommendation is presented for authorized human review
    And no transfer or redirection occurs automatically

  Scenario: AC-009 - Continue triage when ML processing is unavailable for FR-007
    Given the ML component is unavailable
    When a TriageNurse opens a PatientEncounter
    Then ERFlow indicates that no ML recommendation is available
    And the TriageNurse and EmergencyPhysician can continue the normal triage and priority workflow
```

## Traceability Summary

| Requirement | Business goal(s) | Acceptance criteria |
|---|---|---|
| FR-001 | G-001, G-002 | AC-001 |
| FR-002 | G-001, G-002, G-003 | AC-002 |
| FR-003 | G-003 | AC-003 |
| FR-004 | G-004 | AC-004A, AC-004B, AC-004C |
| FR-005 | G-001, G-002 | AC-005 |
| FR-006 | G-005 | AC-006 |
| FR-007 | G-002, G-003, G-004 | AC-002, AC-007, AC-009 |
| FR-008 | G-005 | AC-006, AC-008 |

Rajas
