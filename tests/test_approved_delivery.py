import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from docx import Document
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backup_restore import backup, restore
from diagnostic_engine import CODES
from mevan_test_approval import ApprovalError, read_approval
from mevan_test_report_manifest import prepare_report_manifest
from mevan_test_workspace_api import create_test_router


def review_content(identifier):
    return dict(
        summary=f'Za dijagnostiku {identifier} pregledani su izvori proizvodnje i finansija. Zastoji i škart zahtijevaju dodatnu provjeru početnih pokazatelja prije izbora ograničenog pilota.',
        priority1='Provjeriti evidenciju zastoja O03 s voditeljem održavanja i utvrditi početno trajanje prekida.',
        priority2='Uskladiti trošak škarta F06 s kontrolingom i dokumentovati osnovicu prije određivanja cilja.',
        priority3='Pregledati plan kapaciteta P03 s planerom i povezati kašnjenja s konkretnim narudžbama.',
        month1='U prvih 30 dana voditelj održavanja prikuplja evidenciju zastoja i potvrđuje početni pokazatelj sati prekida.',
        month2='Do 60. dana proizvodnja provodi ograničeni pilot održavanja i sedmično prati promjenu trajanja zastoja.',
        month3='Do 90. dana kontroling i konsultant porede rezultate pilota s osnovicom i dokumentuju preporuku narednih aktivnosti.',
    )


def diagnostic(identifier):
    records = [dict(criterion_id=code, score=3, verification_status="provjereno",
                    assessor_id="QA", evidence_reference="Dokaz " + code, source_id="test",
                    reference_period_start="2026-01-01", reference_period_end="2026-06-30",
                    assessment_version="1", timestamp="2026-07-01", verification_audit_ref="audit")
               for code in sorted(CODES)]
    return dict(id=identifier, quality_records=records, risk_reviews=dict(O14="reviewed", L09="reviewed", M08="reviewed"),
                consultant_review=review_content(identifier))


class ApprovedDelivery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "test.db"
        app = FastAPI()
        app.include_router(create_test_router(str(self.path), lambda r:True, lambda r:True, "test-konsultant"))
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.workspace = {"companies":[{"id":"firma","diagnostics":[diagnostic("prva"), diagnostic("druga")]}]}
        self.save(0)

    def save(self, revision):
        response = self.client.put("/api/test/v2/workspace", json={"expected_revision":revision,"workspace":self.workspace})
        self.assertEqual(response.status_code, 200, response.text)

    def approve(self):
        return self.client.post("/api/test/v2/approvals", json={"expected_revision":1,"company_index":0,"diagnostic_index":0})

    def test_immutable_reports_and_backup(self):
        approval = self.approve().json()["approval_id"]
        self.workspace["companies"][0]["diagnostics"][0]["consultant_review"]["summary"]="kasnija izmjena"
        self.save(1)
        with sqlite3.connect(self.path) as db:
            with self.assertRaises(ApprovalError):
                prepare_report_manifest(db, approval, 0, 1)
        for view in ("executive","detailed"):
            for fmt in ("docx","pdf"):
                r = self.client.get(f"/api/test/v2/approvals/{approval}/{view}/{fmt}")
                self.assertEqual(r.status_code, 200)
                if fmt=="docx":
                    text="\n".join(p.text for p in Document(io.BytesIO(r.content)).paragraphs)
                    self.assertIn("Za dijagnostiku prva",text)
                    self.assertNotIn("Za dijagnostiku druga",text)
                    self.assertNotIn("kasnija izmjena",text)
                    self.assertEqual("Dokaz F01" in text, view=="detailed")
                else:
                    self.assertTrue(r.content.startswith(b"%PDF"))
        dest=self.path.with_name("backup.db")
        restored=self.path.with_name("restored.db")
        backup(self.path,dest)
        restore(dest,restored)
        with sqlite3.connect(restored) as db:
            self.assertEqual(prepare_report_manifest(db,approval,0,0)["diagnostic_id"],"prva")

    def test_unbound_legacy_approval_requires_review(self):
        self.approve()
        raw=json.dumps(self.workspace)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE diagnostic_approvals_test SET snapshot_json=?,sha256=?", (raw,hashlib.sha256(raw.encode()).hexdigest()))
            with self.assertRaises(ApprovalError):
                read_approval(db,1)
