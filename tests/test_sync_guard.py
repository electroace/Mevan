"""Run with: python -m unittest discover -s tests -p 'test_sync_guard.py'"""
import sqlite3
import unittest
from mevan_sync_guard import (
    InvalidWorkspace, RevisionConflict, init_test_store,
    read_test_workspace, save_test_workspace,
)


class SyncGuardTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        init_test_store(self.db)
        self.workspace = {"companies": [{"diagnostics": []}]}

    def tearDown(self):
        self.db.close()

    def test_initial_revision(self):
        self.assertEqual(read_test_workspace(self.db)["revision"], 0)

    def test_first_save(self):
        self.assertEqual(save_test_workspace(self.db, self.workspace, 0), 1)
        self.assertEqual(read_test_workspace(self.db)["workspace"], self.workspace)

    def test_stale_save_rejected_and_data_preserved(self):
        save_test_workspace(self.db, self.workspace, 0)
        newer = {"companies": [{"diagnostics": [{"id": "new"}]}]}
        save_test_workspace(self.db, newer, 1)
        with self.assertRaises(RevisionConflict):
            save_test_workspace(self.db, self.workspace, 1)
        self.assertEqual(read_test_workspace(self.db)["workspace"], newer)
        self.assertEqual(read_test_workspace(self.db)["revision"], 2)

    def test_invalid_revision(self):
        with self.assertRaises(ValueError):
            save_test_workspace(self.db, self.workspace, True)

    def test_invalid_workspace(self):
        with self.assertRaises(InvalidWorkspace):
            save_test_workspace(self.db, {"companies": []}, 0)

    def test_no_changes_to_legacy_table(self):
        self.assertEqual(
            self.db.execute("SELECT name FROM sqlite_master WHERE name='workspace'").fetchone(),
            None,
        )


if __name__ == "__main__":
    unittest.main()
