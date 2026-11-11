import sqlite3
import unittest
from diagnostic_engine import CODES
from mevan_sync_guard import init_test_store, save_test_workspace
from mevan_test_approval import init_approval_store, approve_workspace
from mevan_test_report_manifest import prepare_report_manifest, ReportPreparationBlocked
from mevan_test_approval import ApprovalError


class ReportManifestTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        init_test_store(self.db)
        init_approval_store(self.db)

    def tearDown(self):
        self.db.close()

    def approve(self, diagnostic):
        workspace = {"companies": [{"diagnostics": [diagnostic]}]}
        save_test_workspace(self.db, workspace, 0)
        return approve_workspace(self.db, 1, "reviewer", 0, 0)["approval_id"]

    def test_missing_quality_records_fail_closed(self):
        with self.assertRaises(ApprovalError):
            self.approve({"id": "d1"})

    def test_blocked_quality_gate_refuses_manifest(self):
        with self.assertRaises(ApprovalError):
            self.approve({"quality_records": [], "risk_reviews": {}})

    def test_warning_refuses_manifest(self):
        records = [{"criterion_id": code, "score": 2, "verification_status": "samoprocjena"}
                   for code in sorted(CODES)]
        reviews = {code: "reviewed" for code in ("O14", "L09", "M08")}
        with self.assertRaises(ApprovalError):
            self.approve({"id": "test-a", "quality_records": records, "risk_reviews": reviews})

    def test_pass_produces_snapshot_bound_manifest(self):
        records = [{
            "criterion_id": code, "score": 2, "verification_status": "provjereno",
            "assessor_id": "reviewer", "evidence_reference": "ref",
            "source_id": "src", "reference_period_start": "2026-01-01",
            "reference_period_end": "2026-06-30", "assessment_version": "1",
            "timestamp": "2026-07-01", "verification_audit_ref": "audit",
        } for code in sorted(CODES)]
        reviews = {code: "reviewed" for code in ("O14", "L09", "M08")}
        approval_id = self.approve({"id": "test-a", "quality_records": records, "risk_reviews": reviews})
        result = prepare_report_manifest(self.db, approval_id, 0, 0)
        self.assertEqual(result["status"], "READY_FOR_TEST_RENDER")
        self.assertEqual(result["workspace_revision"], 1)
        self.assertEqual(len(result["snapshot_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
