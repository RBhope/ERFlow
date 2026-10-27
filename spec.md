# Description

ERFlow is a proposed machine-learning (ML)-assisted decision-support system for emergency department (ED) triage and patient flow. It helps healthcare professionals record patient assessment information, review an advisory urgency recommendation and its explanation, establish a clinical triage priority, and reassess patients waiting for care. It also supports the review of capacity-aware routing recommendations using patient priority, ED capacity, and travel time. Authorized healthcare professionals retain final authority over triage decisions, and routing recommendations require a human decision. The project does not cover diagnosis, treatment planning, prescriptions, billing, or complete hospital management. The ML model, data, and routing methods are to be selected and evaluated during development.

# Goals

1. Assess patient urgency effectively using relevant patient information and decision support.
2. Prioritize patients appropriately and support reassessment when their condition changes.
3. Support safe and timely emergency care decisions with understandable, human-centered recommendations.
4. Maintain clinical control over final triage decisions.
5. Support appropriate patient routing by considering emergency department capacity and travel time.

# Domain Model

## Actors

- **Triage Nurse:** Records and updates patient assessments, reviews urgency recommendations, and monitors the patient queue.
- **Emergency Physician:** Reviews patient and recommendation information and confirms or overrides the recommended priority.
- **ER Administrator:** Reviews emergency department capacity and advisory routing recommendations.
- **ERFlow System (system under specification):** Processes assessments, presents recommendations and explanations, and maintains triage and patient-flow information; it is not an external human user.
- **Patient:** The person receiving emergency care and the subject of an encounter; not a direct ERFlow user in these requirements.

## Objects

- **Patient:** The person associated with a PatientEncounter and its assessment information.
- **PatientEncounter:** An emergency-care encounter associated with a patient, assessments, priority, and any routing recommendation.
- **TriageAssessment:** Information collected for an encounter, including the main complaint, symptoms, vital signs, medical history, allergies, medications, and clinical observations.
- **Symptom:** A reported or observed indication of the patient's condition.
- **VitalSign:** A measurement such as heart rate, blood pressure, oxygen saturation, respiratory rate, or temperature.
- **MedicalHistory, Allergy, Medication, ClinicalObservation:** Information associated with a triage assessment.
- **UrgencyRecommendation:** An advisory ML-generated estimate of the urgency of an assessment; it is not the final clinical priority.
- **RecommendationExplanation:** The main patient factors presented to help a clinician understand an urgency recommendation.
- **TriagePriority:** The priority confirmed or selected by an authorized clinician for an encounter.
- **PatientQueue:** The collection of encounters waiting for care, displayed by their current triage priority.
- **ERFacility:** An emergency-care facility that may be considered for routing.
- **CapacityStatus:** Facility information such as available treatment spaces, patient load, and estimated wait time.
- **RoutingRecommendation:** An advisory recommendation for an ERFacility based on patient priority, capacity, and travel time.
- **Reassessment:** An updated assessment of a waiting patient when their condition changes.

# Functional Requirements

**FR-001 — Triage assessment.** As a Triage Nurse, I want to record a patient's symptoms, vital signs, and other triage assessment information, so that I can assess patient urgency effectively.

**FR-002 — Urgency recommendation.** As a Triage Nurse, I want to review an ML-assisted urgency recommendation, so that I can prioritize patients appropriately.

**FR-003 — Recommendation explanation.** As a Triage Nurse, I want to see the main patient factors that influenced the urgency recommendation, so that I can receive understandable decision support.

**FR-004 — Clinical confirmation and override.** As an Emergency Physician, I want to confirm or override the recommended triage priority, so that I can maintain clinical control.

**FR-005 — Priority view and reassessment.** As a Triage Nurse, I want to view patient encounters by triage priority and update an assessment when a patient's condition changes, so that I can prioritize patients appropriately.

**FR-006 — Capacity and routing review.** As an ER Administrator, I want to review capacity information and routing recommendations, so that I can support appropriate patient routing.

**FR-007 — ML processing and human authority.** The system shall process available triage assessment information using the selected ML model or models and generate an advisory urgency recommendation. The system shall not automatically assign the final triage priority. This supports safe and timely care decisions while maintaining clinical control.

**FR-008 — Capacity-aware routing logic.** The system shall consider the patient's triage priority, ER facility capacity status, and travel time when generating a routing recommendation. This supports appropriate patient routing.

# Acceptance Criteria

Each scenario has a unique acceptance-criterion ID and references the functional requirement it verifies.

### AC-001 — Record an assessment (FR-001)

```gherkin
Scenario: AC-001 - Record a triage assessment
Given a Triage Nurse has opened a PatientEncounter
When the nurse enters the patient's triage information
And submits the TriageAssessment
Then ERFlow stores the TriageAssessment for the PatientEncounter
```

### AC-002 — Review an urgency recommendation (FR-002)

```gherkin
Scenario: AC-002 - Review an urgency recommendation
Given a TriageAssessment is available
When ERFlow processes the available triage information
Then ERFlow displays an advisory UrgencyRecommendation
```

### AC-003 — View the recommendation explanation (FR-003)

```gherkin
Scenario: AC-003 - View recommendation explanation
Given an UrgencyRecommendation has been generated
When the Triage Nurse reviews the recommendation
Then ERFlow displays the main patient factors that influenced it
```

### AC-004 — Confirm the recommended priority (FR-004)

```gherkin
Scenario: AC-004 - Confirm recommended priority
Given an Emergency Physician is reviewing a PatientEncounter
And an UrgencyRecommendation is available
When the physician confirms the suggested priority
Then ERFlow saves it as the TriagePriority
And updates the PatientQueue
```

### AC-005 — Override the recommended priority (FR-004)

```gherkin
Scenario: AC-005 - Override recommended priority
Given an Emergency Physician is reviewing a PatientEncounter
And an UrgencyRecommendation is available
When the physician selects another priority
And records an override reason
Then ERFlow saves the clinician-selected TriagePriority
And updates the PatientQueue
```

### AC-006 — View patients by priority (FR-005)

```gherkin
Scenario: AC-006 - View waiting patients by priority
Given PatientEncounter records with a clinically assigned TriagePriority are in the PatientQueue
When the Triage Nurse opens the PatientQueue
Then ERFlow displays the waiting encounters by their current TriagePriority
```

### AC-007 — Reassess a waiting patient (FR-005)

```gherkin
Scenario: AC-007 - Reassess a waiting patient
Given a PatientEncounter is in the PatientQueue
When the Triage Nurse records changed symptoms or vital signs
And submits the updated TriageAssessment
Then ERFlow saves the updated TriageAssessment for the PatientEncounter
And provides an updated advisory UrgencyRecommendation for clinical review
And does not automatically change the current TriagePriority
```

### AC-008 — Review capacity-aware routing (FR-006)

```gherkin
Scenario: AC-008 - Review capacity-aware routing
Given CapacityStatus is available for participating ERFacility options
When the ER Administrator requests a routing review
Then ERFlow displays an advisory RoutingRecommendation for the PatientEncounter
And does not automatically initiate a patient transfer
```

### AC-009 — Preserve human clinical authority (FR-007)

```gherkin
Scenario: AC-009 - Preserve human clinical authority
Given ERFlow has generated an UrgencyRecommendation
When the recommendation is displayed
Then ERFlow does not automatically assign the final TriagePriority
```

### AC-010 — Display routing inputs (FR-008)

```gherkin
Scenario: AC-010 - Show routing factors
Given a clinically assigned TriagePriority is available for a PatientEncounter
And CapacityStatus and travel time are available for the ERFacility options
When ERFlow generates a RoutingRecommendation
Then ERFlow displays the recommended ERFacility
And shows the TriagePriority, CapacityStatus, and travel time used in the routing review
```
