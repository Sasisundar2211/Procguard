import unittest
from datetime import datetime, timedelta
from app.core.timeline_classification import classify_timeline_cell, TimelineStatus, compute_eos_status

class TestTimelineClassification(unittest.TestCase):
    def setUp(self):
        self.deviations = [
            {
                "id": "dev-1",
                "stage": "QA BMR Review",
                "valid_from_day": 10,
                "valid_until_day": 20,
                "approved_by": "qa@corp.com",
                "resolved_at": None,
                "superseded_by_lir": False
            }
        ]
        self.lirs = [{"stage": "QA BMR Review", "day": 15}]

    def test_deviation_classification(self):
        # Case 1: Within deviation window
        status = classify_timeline_cell(
            stage_name="QA BMR Review",
            day=12,
            planned_day=12,
            deviations=self.deviations
        )
        self.assertEqual(status, TimelineStatus.DEVIATION)

    def test_lir_precedence(self):
        # Case 2: LIR overrides Deviation at Day 15
        status = classify_timeline_cell(
            stage_name="QA BMR Review",
            day=15,
            planned_day=15,
            deviations=self.deviations,
            lirs=self.lirs
        )
        self.assertEqual(status, TimelineStatus.LIR)

    def test_deviation_resolution(self):
        # Case 3: Resolved deviation returns to normal status
        resolved_deviations = [dict(d, resolved_at=datetime.now()) for d in self.deviations]
        status = classify_timeline_cell(
            stage_name="QA BMR Review",
            day=12,
            planned_day=10,
            actual_day=12,
            deviations=resolved_deviations
        )
        self.assertEqual(status, TimelineStatus.OVER_TIME)

    def test_window_boundaries(self):
        # Case 4: Outside window
        status = classify_timeline_cell(
            stage_name="QA BMR Review",
            day=22,
            planned_day=22,
            deviations=self.deviations
        )
        self.assertEqual(status, TimelineStatus.ON_TIME)

class TestEOSClassification(unittest.TestCase):
    def setUp(self):
        self.deviations = [
            {
                "id": "dev-1",
                "stage": "Audit",
                "valid_from_day": 10,
                "valid_until_day": 20,
                "resolved_at": None,
                "superseded_by_lir": False
            }
        ]

    def test_on_time_eos(self):
        status, dev_id = compute_eos_status(0, "Audit", 15, self.deviations)
        self.assertEqual(status, "ON_TIME")

    def test_overdue_with_deviation(self):
        status, dev_id = compute_eos_status(5, "Audit", 15, self.deviations)
        self.assertEqual(status, "DEVIATION")
        self.assertEqual(dev_id, "dev-1")

    def test_overdue_without_deviation(self):
        status, dev_id = compute_eos_status(5, "Audit", 25, self.deviations)
        self.assertEqual(status, "EOS")

    def test_overdue_with_resolved_deviation(self):
        resolved_devs = [dict(d, resolved_at=datetime.now()) for d in self.deviations]
        status, dev_id = compute_eos_status(5, "Audit", 15, resolved_devs)
        self.assertEqual(status, "EOS")

if __name__ == '__main__':
    unittest.main()
