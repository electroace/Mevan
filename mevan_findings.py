"""Lanac nalaza za model 65/6: ocjena → dokaz → nalaz → uzročna hipoteza i alternativa → posljedica → preporuka → vlasnik → KPI.

Pravila (specifikacija Diagnostic Engine v1, poglavlja 4 i 5):
- Ocjena je cijeli broj 0–5 ili nepoznata. Nepoznato nikad nije nula i ne stvara nalaz o slabosti, nego prazninu u dokazima.
- Niska ocjena ne dokazuje uzrok. Uzrok je HIPOTEZA dok konsultant izričito ne potvrdi uzrok, navede dokaz uzroka
  i zabilježi razmotreno konkurentsko objašnjenje, i to na dokazom potvrđenom kriteriju koji nije simulacija.
- Svaki nalaz nosi prirodu podatka: SIMULIRANO, POTVRĐENO (potvrdio konsultant; nije nezavisna verifikacija) ili NEPOTVRĐENO.
- Ovdje se ništa ne računa u novcu. Finansijski model se samo navodi, uz status iz kataloga.
Tekst hipoteze posljedice, preporuke, vlasnika i uslova dolazi iz kataloga metodologije; tekst nalaza i uzroka unosi konsultant.
"""
import mevan_methodology

EVIDENCE_STATUS = {'confirmed': 'POTVRDIO_KONSULTANT', 'review': 'U_PROVJERI', 'missing': 'DOKAZ_NEDOSTUPAN'}
TRACKED_FIELDS = ('score', 'proof', 'applicable', 'cause_status')


def _text(value, limit=1200):
    return str(value or '').strip()[:limit]


def build(assess, simulated=False):
    """Nalazi za sve kriterije modela 65/6 iz unesenih procjena. Ne mijenja ulaz."""
    if not isinstance(assess, dict):
        raise ValueError('Neispravne procjene')
    catalogue = mevan_methodology.load('v2')
    findings, counts = [], {}
    for criterion in catalogue['criteria']:
        entry = assess.get(criterion['code'])
        entry = entry if isinstance(entry, dict) else {}
        score = mevan_methodology._score(entry.get('score'))
        evidence = _text(entry.get('evidence'))
        proof = entry.get('proof')
        confirmed = proof == 'confirmed' and score is not None and bool(evidence)
        if entry.get('applicable') == 'no':
            kind = 'NIJE_PRIMJENJIVO'
        elif score is None or not evidence:
            kind = 'PRAZNINA_U_DOKAZIMA'
        elif score <= 2:
            kind = 'KANDIDAT_SLABOST'
        elif score == 3:
            kind = 'DJELIMICNO_RAZVIJENO'
        else:
            kind = 'KANDIDAT_SNAGA' if confirmed else 'NEPOTVRDJENA_SNAGA'
        nature = 'SIMULIRANO' if simulated else 'POTVRĐENO' if confirmed else 'NEPOTVRĐENO'
        alternative, cause_evidence = _text(entry.get('alternative')), _text(entry.get('cause_evidence'), 500)
        blockers = []
        if entry.get('cause_status') != 'verified':
            blockers.append('konsultant nije označio uzrok kao potvrđen')
        if not cause_evidence:
            blockers.append('nije naveden dokaz uzroka')
        if not alternative:
            blockers.append('nije razmotreno konkurentsko objašnjenje')
        if not confirmed:
            blockers.append('kriterij nema potvrđen dokaz i ocjenu')
        if simulated:
            blockers.append('podaci su simulacija')
        finding = {
            'code': criterion['code'], 'module': criterion['module'], 'name': criterion['name'], 'kind': kind, 'nature': nature,
            'score': score, 'level_description': criterion['anchors'][score] if score is not None else '',
            'evidence': {'status': EVIDENCE_STATUS.get(proof, 'NIJE_PROVJERENO'), 'text': evidence, 'required': criterion['evidence']},
            'claim': _text(entry.get('finding')),
            'cause': {'id': criterion['causal_hypothesis_id'], 'status': 'HIPOTEZA' if blockers else 'POTVRĐEN_UZROK',
                      'not_verified_because': blockers, 'evidence': cause_evidence, 'alternative': alternative},
            'consequence': {'status': 'HIPOTEZA', 'text': criterion['consequence_hypothesis']},
            'recommendation': _text(entry.get('recommendation')) or criterion['recommendation'],
            'owner_role': criterion['owner'], 'kpi': _text(entry.get('kpi'), 500) or criterion['kpi'],
            'required_check': criterion['required_check'], 'gate': criterion['gate'],
            'financial': {'model': criterion['financial']['model'], 'family': criterion['financial']['family'],
                          'status': criterion['financial']['status'], 'amount': None},
        }
        if kind == 'NIJE_PRIMJENJIVO':
            finding['not_applicable_reason'] = _text(entry.get('na_reason') or entry.get('evidence'))
        if kind == 'PRAZNINA_U_DOKAZIMA':
            # Nedostajući dokaz nije slabost procesa, nego prvi korak: uspostaviti evidenciju koja se traži.
            finding['first_step'] = 'Pribaviti: ' + criterion['evidence']
        if kind == 'KANDIDAT_SLABOST':
            missing = [label for label, present in (('nalaz konsultanta', finding['claim']), ('dokaz', evidence),
                                                    ('konkurentsko objašnjenje', alternative)) if not present]
            finding['publication'] = {'ready': not missing, 'missing': missing}
        findings.append(finding)
        counts[kind] = counts.get(kind, 0) + 1
    weak = [f for f in findings if f['kind'] == 'KANDIDAT_SLABOST']
    return {
        'methodology': 'v2', 'methodology_status': catalogue['status'], 'simulated': bool(simulated),
        'maturity': mevan_methodology.maturity('v2', assess), 'counts': counts, 'findings': findings,
        'verified_causes': sum(1 for f in findings if f['cause']['status'] == 'POTVRĐEN_UZROK'),
        'gate_logic_check': {'ready': bool(weak) and all(f['publication']['ready'] for f in weak),
                             'not_ready': [f['code'] for f in weak if not f['publication']['ready']]},
        'limitations': ['Uzroci su hipoteze dok nisu potvrđeni dokazom i dok nije razmotreno konkurentsko objašnjenje.',
                        'Potvrda konsultanta nije nezavisna verifikacija.', 'Finansijski efekti se u ovoj fazi ne računaju.',
                        'Metodologija 65/6 je nacrt: mapiranja čekaju stručnu potvrdu.'],
    }


def assessment_changes(previous, current, limit=100):
    """Promjene ocjene, statusa dokaza, primjenjivosti i statusa uzroka u dijagnostikama 65/6, za revizijski dnevnik.

    Bilježe se samo nazivi polja i stare/nove vrijednosti tih polja; tekst dokaza i nalaza se ne upisuje u dnevnik.
    """
    def index(workspace):
        found = {}
        for company in (workspace or {}).get('companies', []) if isinstance(workspace, dict) else []:
            for diagnostic in company.get('diagnostics', []) if isinstance(company, dict) else []:
                if isinstance(diagnostic, dict) and diagnostic.get('methodology') == 'v2' and isinstance(diagnostic.get('assess'), dict):
                    found[str(diagnostic.get('id'))] = diagnostic['assess']
        return found
    before, after, changes = index(previous), index(current), []
    for diagnostic_id, assess in after.items():
        old = before.get(diagnostic_id, {})
        for code, entry in assess.items():
            if not isinstance(entry, dict):
                continue
            previous_entry = old.get(code) if isinstance(old.get(code), dict) else {}
            fields = {field: [previous_entry.get(field), entry.get(field)] for field in TRACKED_FIELDS
                      if previous_entry.get(field) != entry.get(field)}
            if fields:
                changes.append({'diagnostic': diagnostic_id, 'criterion': str(code)[:8], 'changes': fields})
                if len(changes) >= limit:
                    return changes
    return changes
