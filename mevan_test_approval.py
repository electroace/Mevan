"""TEST-only immutable approved diagnostic snapshots.

Separate SQLite table; no writes to legacy workspace or existing diagnostics.
Approval requires explicit reviewer and current workspace revision.
"""
import hashlib
import json
import sqlite3
import time
from mevan_sync_guard import read_test_workspace, RevisionConflict
from mevan_report_gate import evaluate_report_gate
from mevan_report_model import freeze_model, has_simulated_inputs

class ApprovalError(Exception):
    pass

def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def init_approval_store(db: sqlite3.Connection):
    db.execute("""CREATE TABLE IF NOT EXISTS diagnostic_approvals_test (
        approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_revision INTEGER NOT NULL,
        snapshot_json TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        reviewer_id TEXT NOT NULL,
        approved_at INTEGER NOT NULL
    )""")
    db.commit()

def approve_workspace(db: sqlite3.Connection, expected_revision: int, reviewer_id: str,
                      company_index: int, diagnostic_index: int) -> dict:
    if type(expected_revision) is not int or expected_revision < 1:
        raise ApprovalError("Neispravna očekivana revizija")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ApprovalError("Nedostaje konsultant")
    if type(company_index) is not int or type(diagnostic_index) is not int or company_index < 0 or diagnostic_index < 0:
        raise ApprovalError("Neispravni indeksi dijagnostike")
    db.execute("BEGIN IMMEDIATE")
    try:
        state = read_test_workspace(db)
        if state["revision"] != expected_revision or state["workspace"] is None:
            raise RevisionConflict("Radni prostor je promijenjen; ponovo pregledati")
        try:
            diagnostic = state["workspace"]["companies"][company_index]["diagnostics"][diagnostic_index]
            records = diagnostic["quality_records"]
            reviews = diagnostic["risk_reviews"]
            claims = diagnostic.get("finance_claims", [])
        except (KeyError, IndexError, TypeError) as exc:
            raise ApprovalError("Nedostaju podaci za Quality Gate") from exc
        mode=diagnostic.get('report_mode','real')
        company=state['workspace']['companies'][company_index]
        if mode not in ('real','demo'):
            raise ApprovalError('Odaberite stvarni ili DEMO način izvještaja')
        if mode=='real' and has_simulated_inputs(company,diagnostic):
            raise ApprovalError('Simulirani ulazi zahtijevaju eksplicitan DEMO način; nisu stvarni provjereni nalazi')
        gate = evaluate_report_gate(
            records, expected_revision, expected_revision, reviewer_id,
            risk_reviews=reviews, finance_claims=claims, mode=mode,
        )
        if gate["status"] != "PASS":
            details = gate["issues"] + gate["warnings"]
            failed = [r["criterion_id"] for r in gate["quality"]["results"] if r["errors"]]
            if failed:
                details.append("Provjerite kriterije: " + ", ".join(str(code) for code in failed))
            raise ApprovalError(gate["status"] + " · " + " · ".join(details))
        diagnostic_id = diagnostic.get("id")
        if not isinstance(diagnostic_id, str) or not diagnostic_id.strip():
            raise ApprovalError("Za odobrenje je potreban trajni ID dijagnostike")
        raw = _canonical({
            "format": "mevan-bound-approval-v2",
            "report_mode": mode,
            "report_model": freeze_model(diagnostic),
            "workspace": state["workspace"],
            "company_index": company_index,
            "diagnostic_index": diagnostic_index,
            "diagnostic_id": diagnostic_id,
        })
        digest = hashlib.sha256(raw).hexdigest()
        cursor = db.execute(
            "INSERT INTO diagnostic_approvals_test(workspace_revision,snapshot_json,sha256,reviewer_id,approved_at) VALUES(?,?,?,?,?)",
            (expected_revision, raw.decode("utf-8"), digest, reviewer_id.strip(), int(time.time())),
        )
        db.commit()
        return {"approval_id": cursor.lastrowid, "workspace_revision": expected_revision, "sha256": digest, "reviewer_id": reviewer_id.strip(), "quality_gate": "PASS", "report_mode": mode}
    except Exception:
        db.rollback()
        raise

def read_approval(db: sqlite3.Connection, approval_id: int) -> dict:
    if type(approval_id) is not int or approval_id < 1:
        raise ApprovalError("Neispravan ID odobrenja")
    row = db.execute(
        "SELECT workspace_revision,snapshot_json,sha256,reviewer_id,approved_at FROM diagnostic_approvals_test WHERE approval_id=?",
        (approval_id,),
    ).fetchone()
    if not row:
        raise ApprovalError("Odobrenje ne postoji")
    revision, raw, digest, reviewer, approved_at = row
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != digest:
        raise ApprovalError("Integritet odobrenog snimka nije potvrđen")
    snapshot = json.loads(raw)
    if snapshot.get("format") not in ("mevan-bound-approval-v1","mevan-bound-approval-v2"):
        raise ApprovalError("Ranije odobrenje nema vezu s dijagnostikom. Potreban je novi pregled.")
    mode=snapshot.get('report_mode','real') if snapshot['format']=='mevan-bound-approval-v2' else 'real'
    model=snapshot.get('report_model')
    if mode not in ('real','demo') or (snapshot['format']=='mevan-bound-approval-v2' and
        (not isinstance(model,dict) or model.get('version')!=2 or not isinstance(model.get('result'),dict))):
        raise ApprovalError('Zaključani snimak nema podržan način ili obračun izvještaja')
    if snapshot['format']=='mevan-bound-approval-v2':
        try:
            diagnostic=snapshot['workspace']['companies'][snapshot['company_index']]['diagnostics'][snapshot['diagnostic_index']]
            if diagnostic.get('report_mode','real')!=mode:raise ApprovalError('Način snimka nije usklađen s dijagnostikom')
        except (KeyError,IndexError,TypeError) as exc:raise ApprovalError('Neispravna veza zaključane dijagnostike') from exc
    return {"company_index": snapshot["company_index"], "diagnostic_index": snapshot["diagnostic_index"],
            'report_mode':mode,'report_model':snapshot.get('report_model'),'policy_version':2 if snapshot['format']=='mevan-bound-approval-v2' else 1,
            "diagnostic_id": snapshot["diagnostic_id"], "approval_id": approval_id, "workspace_revision": revision, "workspace": snapshot["workspace"], "sha256": digest, "reviewer_id": reviewer, "approved_at": approved_at}
