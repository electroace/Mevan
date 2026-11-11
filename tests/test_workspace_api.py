"""TEST-only integration tests: no production server, no real data."""
import os
import tempfile
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mevan_test_workspace_api import create_test_router


class TestWorkspaceAPI(unittest.TestCase):
    def setUp(self):
        f = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        self.db_path = f.name
        f.close()
        self.allowed = True
        self.origin_allowed = True
        self.app = FastAPI()
        self.app.include_router(create_test_router(
            self.db_path,
            authorize=lambda req: self.allowed,
            verify_write_origin=lambda req: self.origin_allowed,
        ))
        self.client = TestClient(self.app)
        self.data = {"companies": [{"diagnostics": []}]}

    def tearDown(self):
        self.client.close()
        os.unlink(self.db_path)

    def test_missing_security_callbacks_rejected(self):
        with self.assertRaises(ValueError):
            create_test_router(self.db_path, None, None)

    def test_authentication_required(self):
        self.allowed = False
        self.assertEqual(self.client.get("/api/test/v2/workspace").status_code, 401)
        self.assertEqual(self.client.put("/api/test/v2/workspace", json={
            "workspace": self.data, "expected_revision": 0,
        }).status_code, 401)

    def test_write_origin_required(self):
        self.origin_allowed = False
        response = self.client.put("/api/test/v2/workspace", json={
            "workspace": self.data, "expected_revision": 0,
        })
        self.assertEqual(response.status_code, 403)

    def test_conflict_returns_409_without_overwrite(self):
        url = "/api/test/v2/workspace"
        first = self.client.put(url, json={"workspace": self.data, "expected_revision": 0})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["revision"], 1)
        newer = {"companies": [{"diagnostics": [{"id": "v2"}]}]}
        second = self.client.put(url, json={"workspace": newer, "expected_revision": 1})
        self.assertEqual(second.status_code, 200)
        stale = self.client.put(url, json={"workspace": self.data, "expected_revision": 1})
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.json()["detail"]["current_revision"], 2)
        self.assertEqual(self.client.get(url).json()["workspace"], newer)

    def test_boolean_revision_rejected(self):
        response = self.client.put("/api/test/v2/workspace", json={
            "workspace": self.data, "expected_revision": True,
        })
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
