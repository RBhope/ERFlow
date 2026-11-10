from unittest import TestCase
from unittest.mock import Mock

from modules import assessment, priority_queue, recommendation
from modules.data_store import DataStore


class AcceptanceTests(TestCase):
    def setUp(self):
        self.store = Mock(spec=DataStore)

    def test_T_001_record_assessment(self):
        self.store.get_role.return_value = "Triage Nurse"

        data = {
            "assessment_id": "A1",
            "complaint": "headache",
            "symptoms": ["dizziness"],
            "vitals": {"heart_rate_bpm": 90},
        }

        try:
            result = assessment.save_assessment("E1", "N1", data, self.store)
        except NotImplementedError:
            self.fail("T-001: Assessment saving is not implemented yet.")

        self.assertEqual(result["assessment_id"], "A1")
        self.store.save_record.assert_called()

    def test_T_003_view_explanation(self):
        self.store.get_role.return_value = "Triage Nurse"
        self.store.get_records.return_value = [
            {
                "encounter_id": "E1",
                "priority": "TEST-PRIORITY-A",
                "advisory": True,
                "factors": ["dizziness"],
            }
        ]

        try:
            result = recommendation.get_recommendation("E1", "N1", self.store)
        except NotImplementedError:
            self.fail("T-003: Recommendation retrieval is not implemented yet.")

        self.assertEqual(result["encounter_id"], "E1")
        self.assertTrue(result["advisory"])
        self.assertIn("dizziness", result["factors"])

    def test_T_005_override_priority(self):
        self.store.get_role.return_value = "Emergency Physician"
        self.store.get_records.return_value = [
            {
                "encounter_id": "E1",
                "priority": "TEST-PRIORITY-A",
                "advisory": True,
            }
        ]

        decision = {
            "action": "override",
            "priority": "TEST-PRIORITY-B",
            "override_reason": "Clinical assessment",
        }

        try:
            result = priority_queue.record_priority(
                "E1", "P1", decision, self.store
            )
        except NotImplementedError:
            self.fail("T-005: Priority recording is not implemented yet.")

        self.assertEqual(result["encounter_id"], "E1")
        self.assertEqual(result["priority"], "TEST-PRIORITY-B")
        self.assertEqual(result["override_reason"], "Clinical assessment")
        self.store.save_record.assert_called()