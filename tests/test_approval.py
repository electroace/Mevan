import sqlite3
import unittest
from mevan_sync_guard import init_test_store, save_test_workspace, RevisionConflict
from diagnostic_engine import CODES
from mevan_test_approval import init_approval_store, approve_workspace, read_approval, ApprovalError

class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        init_test_store(self.db)
        init_approval_store(self.db)
        records = [{
            "criterion_id": code, "score": 2, "verification_status": "provjereno",
            "assessor_id": "reviewer", "evidence_reference": "ref", "source_id": "src",
            "reference_period_start": "2026-01-01", "reference_period_end": "2026-06-30",
            "assessment_version": "1", "timestamp": "2026-07-01",
            "verification_audit_ref": "audit",
        } for code in sorted(CODES)]
        self.first = {"companies": [{"diagnostics": [{
            "id": "v1", "quality_records": records,
            "risk_reviews": {"O14": "reviewed", "L09": "reviewed", "M08": "reviewed"},
        }]}]}
        save_test_workspace(self.db, self.first, 0)

    def tearDown(self):
        self.db.close()

    def test_approval_snapshot_survives_future_edit(self):
        approval = approve_workspace(self.db, 1, "reviewer", 0, 0)
        save_test_workspace(self.db, {"companies": [{"diagnostics": [{"id": "v2"}]}]}, 1)
        self.assertEqual(read_approval(self.db, approval["approval_id"])["workspace"], self.first)

    def test_stale_revision_rejected(self):
        with self.assertRaises(RevisionConflict):
            approve_workspace(self.db, 2, "reviewer", 0, 0)

    def test_reviewer_required(self):
        with self.assertRaises(ApprovalError):
            approve_workspace(self.db, 1, " ", 0, 0)

    def test_corrupted_snapshot_rejected(self):
        approval = approve_workspace(self.db, 1, "reviewer", 0, 0)
        self.db.execute("UPDATE diagnostic_approvals_test SET snapshot_json='{}' WHERE approval_id=?", (approval["approval_id"],))
        with self.assertRaises(ApprovalError):
            read_approval(self.db, approval["approval_id"])

    def test_incomplete_diagnostic_cannot_be_approved(self):
        self.db.execute("DELETE FROM workspace_test_v2")
        save_test_workspace(self.db, {"companies": [{"diagnostics": [{"id": "bad"}]}]}, 0)
        with self.assertRaises(ApprovalError):
            approve_workspace(self.db, 1, "reviewer", 0, 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM diagnostic_approvals_test").fetchone()[0], 0)

    def test_warning_cannot_be_approved(self):
        self.db.execute("DELETE FROM workspace_test_v2")
        records = [{"criterion_id": code, "score": 2, "verification_status": "samoprocjena"} for code in sorted(CODES)]
        save_test_workspace(self.db, {"companies": [{"diagnostics": [{
            "quality_records": records, "risk_reviews": {"O14": "reviewed", "L09": "reviewed", "M08": "reviewed"}
        }]}]}, 0)
        with self.assertRaises(ApprovalError):
            approve_workspace(self.db, 1, "reviewer", 0, 0)

    def test_legacy_table_untouched(self):
        approve_workspace(self.db, 1, "reviewer", 0, 0)
        self.assertIsNone(self.db.execute("SELECT name FROM sqlite_master WHERE name='workspace'").fetchone())

if __name__ == "__main__":
    unittest.main()
