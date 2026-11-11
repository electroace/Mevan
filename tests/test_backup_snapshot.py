"""Run: python -m unittest discover -s tests -p 'test_backup_snapshot.py' -v"""
import copy
import sqlite3
import unittest
from mevan_sync_guard import init_test_store, save_test_workspace, read_test_workspace
from mevan_test_backup import BackupError, export_snapshot, verify_snapshot, restore_snapshot


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        init_test_store(self.db)
        self.original = {"companies": [{"diagnostics": [{"id": "first"}]}]}
        save_test_workspace(self.db, self.original, 0)

    def tearDown(self):
        self.db.close()

    def test_export_verify(self):
        snapshot = export_snapshot(self.db)
        self.assertEqual(verify_snapshot(snapshot)["workspace"], self.original)

    def test_tamper_rejected(self):
        snapshot = export_snapshot(self.db)
        snapshot["payload"]["workspace"]["companies"][0]["diagnostics"].clear()
        with self.assertRaises(BackupError):
            verify_snapshot(snapshot)

    def test_confirmation_required(self):
        snapshot = export_snapshot(self.db)
        with self.assertRaises(BackupError):
            restore_snapshot(self.db, snapshot, 1, "wrong")
        self.assertEqual(read_test_workspace(self.db)["revision"], 1)

    def test_restore_creates_new_revision(self):
        snapshot = export_snapshot(self.db)
        changed = {"companies": [{"diagnostics": [{"id": "second"}]}]}
        save_test_workspace(self.db, changed, 1)
        new_rev = restore_snapshot(self.db, snapshot, 2, "VRATI-TEST-PODATKE")
        self.assertEqual(new_rev, 3)
        self.assertEqual(read_test_workspace(self.db)["workspace"], self.original)

    def test_stale_restore_rejected(self):
        snapshot = export_snapshot(self.db)
        save_test_workspace(self.db, {"companies": [{"diagnostics": []}]}, 1)
        with self.assertRaises(BackupError):
            restore_snapshot(self.db, snapshot, 1, "VRATI-TEST-PODATKE")
        self.assertEqual(read_test_workspace(self.db)["revision"], 2)


if __name__ == "__main__":
    unittest.main()
