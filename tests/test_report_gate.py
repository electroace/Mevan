import unittest
from mevan_report_gate import evaluate_report_gate


class ReportGateTests(unittest.TestCase):
    def test_missing_criteria_blocks(self):
        result = evaluate_report_gate([], 1, 1, "consultant")
        self.assertEqual(result["status"], "BLOCK")

    def test_revision_mismatch_blocks(self):
        result = evaluate_report_gate([], 2, 1, "consultant")
        self.assertIn("Izvještaj nije vezan za odobrenu reviziju", result["issues"])

    def test_reviewer_missing_blocks(self):
        result = evaluate_report_gate([], 1, 1, "")
        self.assertIn("Nedostaje odgovorni konsultant", result["issues"])

    def test_critical_risk_review_blocks(self):
        records = [{"criterion_id": "O14", "verification_status": "nema_podataka", "score": None}]
        result = evaluate_report_gate(records, 1, 1, "consultant")
        self.assertTrue(any("procjena rizika O14" in x for x in result["issues"]))

    def test_unverified_financial_claim_blocks(self):
        result = evaluate_report_gate([], 1, 1, "consultant", finance_claims=[
            {"validation_status": "self_assessed"}
        ])
        self.assertIn("Finansijska korist nije nezavisno potvrđena", result["issues"])

    def test_missing_evidence_warns_even_if_record_not_blocked(self):
        records = [{"criterion_id": "O14", "verification_status": "nema_podataka", "score": None}]
        result = evaluate_report_gate(records, 1, 1, "consultant",
            risk_reviews={"O14": "reviewed", "L09": "reviewed", "M08": "reviewed"})
        self.assertTrue(any("bez dokaza" in w for w in result["warnings"]))

    def test_simulated_data_flagged(self):
        records = [{"criterion_id": "O14", "verification_status": "simulacija",
                    "score": 2, "is_simulated": True}]
        result = evaluate_report_gate(records, 1, 1, "consultant")
        self.assertTrue(any("simulirane podatke" in w for w in result["warnings"]))

    def test_invalid_finance_payload_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_report_gate([], 1, 1, "consultant", finance_claims={"bad": "type"})

    def test_self_assessment_is_not_clean_pass(self):
        records = [{"criterion_id": "F01", "verification_status": "samoprocjena", "score": 3}]
        result = evaluate_report_gate(records, 1, 1, "consultant")
        self.assertTrue(any("samoprocjene" in w for w in result["warnings"]))

    def test_na_requires_scope_warning(self):
        records = [{"criterion_id": "F01", "verification_status": "nije_primjenjivo",
                    "score": None, "na_reason": "Nije relevantno", "na_approved_by": "consultant"}]
        result = evaluate_report_gate(records, 1, 1, "consultant", policy_version=1)
        self.assertTrue(any("N/P" in w for w in result["warnings"]))

    def test_simulated_flag_even_if_status_is_different(self):
        records = [{"criterion_id": "F01", "verification_status": "samoprocjena",
                    "score": 3, "is_simulated": True}]
        result = evaluate_report_gate(records, 1, 1, "consultant")
        self.assertTrue(any("simulirane" in w for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
