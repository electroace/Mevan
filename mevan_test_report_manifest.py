"""TEST-only report preparation: bind quality evaluation to stored approval snapshot.

No publication, DOCX generation, or production integration. Never accept
criterion records or reviewer identity from the report request.
"""
from mevan_test_approval import read_approval, ApprovalError
from mevan_report_gate import evaluate_report_gate


class ReportPreparationBlocked(Exception):
    def __init__(self, result):
        self.result = result
        super().__init__("Quality Gate blokira pripremu izvještaja")


def prepare_report_manifest(db, approval_id: int, company_index: int, diagnostic_index: int) -> dict:
    approval = read_approval(db, approval_id)
    workspace = approval["workspace"]
    try:
        if type(company_index) is not int or type(diagnostic_index) is not int:
            raise ValueError("Indeksi moraju biti cijeli brojevi")
        if company_index < 0 or diagnostic_index < 0:
            raise ValueError("Indeksi ne mogu biti negativni")
        diagnostic = workspace["companies"][company_index]["diagnostics"][diagnostic_index]
        if not isinstance(diagnostic, dict):
            raise ValueError("Neispravna dijagnostika")
        if (company_index, diagnostic_index, diagnostic.get("id")) != (
            approval["company_index"], approval["diagnostic_index"], approval["diagnostic_id"]
        ):
            raise ApprovalError("Odobrenje pripada drugoj dijagnostici")
        records = diagnostic["quality_records"]
        reviews = diagnostic["risk_reviews"]
        claims = diagnostic.get("finance_claims", [])
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ApprovalError("Zaključani snimak nema kompletan Quality Gate zapis") from exc

    gate = evaluate_report_gate(
        records=records,
        approved_revision=approval["workspace_revision"],
        report_revision=approval["workspace_revision"],
        reviewer_id=approval["reviewer_id"],
        risk_reviews=reviews,
        finance_claims=claims,
        mode=approval['report_mode'], policy_version=approval['policy_version'],
    )
    if gate["status"] != "PASS":
        raise ReportPreparationBlocked(gate)
    return {
        "status": "READY_FOR_TEST_RENDER",
        "approval_id": approval_id,
        "workspace_revision": approval["workspace_revision"],
        "snapshot_sha256": approval["sha256"],
        "reviewer_id": approval["reviewer_id"],
        "diagnostic_id": approval["diagnostic_id"],
        "company_index": company_index,
        "diagnostic_index": diagnostic_index,
        "quality_gate": "PASS",
        "report_mode": approval['report_mode'],
        "policy_version": approval['policy_version'],
        "note": "TEST manifest nije dozvola za objavu niti dokaz nezavisne provjere.",
    }
