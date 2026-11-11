"""TEST-only report release gate. Does not certify data or authorize publication.

Deterministic policy on top of existing data_quality_gate.check_batch.
"""
from data_quality_gate import check_batch

CRITICAL = frozenset({"O14", "L09", "M08"})


def evaluate_report_gate(records, approved_revision, report_revision, reviewer_id,
                         risk_reviews=None, finance_claims=None, *, mode='real', policy_version=2):
    if mode not in ('real','demo') or policy_version not in (1,2):
        raise ValueError('Nepoznat način izvještaja ili verzija pravila')
    if not isinstance(records, list):
        raise ValueError("records mora biti lista")
    if not isinstance(approved_revision, int) or isinstance(approved_revision, bool) or approved_revision < 1:
        raise ValueError("approved_revision mora biti pozitivan cijeli broj")
    if risk_reviews is None:
        risk_reviews = {}
    if finance_claims is None:
        finance_claims = []
    if not isinstance(risk_reviews, dict) or not isinstance(finance_claims, list):
        raise ValueError("Neispravan format procjena rizika ili finansijskih tvrdnji")
    issues = []
    warnings = []

    if report_revision != approved_revision:
        issues.append("Izvještaj nije vezan za odobrenu reviziju")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        issues.append("Nedostaje odgovorni konsultant")

    checked = check_batch(records, policy_version=policy_version)
    if checked["blocked"]:
        issues.append(f"Blokirani zapisi: {checked['blocked']}")
    if any(x["status"] == "nepotpuno" for x in checked["results"]):
        warnings.append("Postoje nepotpuni zapisi")
    if len(records) != 61 or len({r.get("criterion_id") for r in records if isinstance(r, dict)}) != 61:
        issues.append("Za završni izvještaj potrebno je 61 jedinstven kriterij")

    if any(r.get("verification_status", "nema_podataka") == "nema_podataka" for r in records if isinstance(r, dict)):
        warnings.append("Postoje kriteriji bez dokaza; potrebna odluka konsultanta")
    if mode=='real' and any(r.get("verification_status") == "simulacija" or r.get("is_simulated") is True for r in records if isinstance(r, dict)):
        warnings.append("Izvještaj sadrži simulirane podatke")
    if any(r.get("verification_status") in ("samoprocjena", "dokumentovano_neprovjereno") for r in records if isinstance(r, dict)):
        warnings.append("Postoje samoprocjene ili dokumentovani ali neprovjereni dokazi")

    by_code = {r.get("criterion_id"): r for r in records if isinstance(r, dict)}
    for code in CRITICAL:
        rec = by_code.get(code)
        if rec is None:
            issues.append(f"Nedostaje kritični kriterij {code}")
            continue
        if rec.get("verification_status") in ("nema_podataka", "samoprocjena") or (mode=='real' and rec.get('verification_status')=='simulacija'):
            warnings.append(f"Kritični kriterij {code} nema nezavisno provjeren dokaz")
        if risk_reviews.get(code) not in ("reviewed", "accepted"):
            issues.append(f"Nedostaje eksplicitna procjena rizika {code}")

    if policy_version==1 and any(r.get("verification_status") == "nije_primjenjivo" for r in records if isinstance(r, dict)):
        warnings.append("Izvještaj sadrži odobrene N/P kriterije; provjeriti obuhvat")

    if mode=='demo':
        if policy_version!=2:
            issues.append('DEMO zahtijeva verzionisani demonstracijski snimak')
        if finance_claims:
            issues.append('DEMO ne može sadržavati potvrđene finansijske tvrdnje')
        if any(r.get('verification_status')!='nije_primjenjivo' and
               (r.get('verification_status')!='simulacija' or r.get('is_simulated') is not True or not str(r.get('evidence_reference') or '').strip())
               for r in records if isinstance(r,dict)):
            issues.append('Svaki primjenjivi DEMO kriterij mora imati ocjenu i jasno označen simulirani dokaz')

    for claim in finance_claims:
        if not isinstance(claim, dict) or claim.get("validation_status") != "independently_verified":
            issues.append("Finansijska korist nije nezavisno potvrđena")
        elif not claim.get("baseline_reference") or not claim.get("calculation_reference"):
            issues.append("Finansijska korist nema referencu na bazu i obračun")

    return {
        "status": "BLOCK" if issues else ("WARN" if warnings else "PASS"),
        "issues": issues,
        "warnings": warnings,
        "quality": checked,
        "approved_revision": approved_revision,
        "report_revision": report_revision,
        "mode": mode,
        "note": "TEST pravila; PASS nije potvrda istinitosti dokaza niti dozvola za objavu.",
    }
