"""Indeks pouzdanosti nalaza za model 65/6. Odvojen je od indeksa zrelosti i nikad ga ne mijenja.

Ponderi i pragovi su iz specifikacije v1.2 i PRIVREMENI su do empirijske kalibracije:
pokrivenost dokazima 30 %, pouzdanost izvora 20 %, usklađenost podataka 20 %, potvrđenost uzroka 15 %,
finansijska sljedivost 15 %; VISOKA ≥ 85, SREDNJA ≥ 65, NISKA < 65.
Ako ijedna komponenta nema podatke, indeks je NEPOZNAT — nedostajući podatak nikad nije nula.

Način na koji se svaka komponenta izvodi iz unesenih podataka je radno pravilo ove implementacije
(specifikacija propisuje šta se mjeri, ali ne i tačan obračun) i čeka potvrdu vlasnika metodologije.
"""
import mevan_finance_v2
import mevan_findings

WEIGHTS = {'evidence_coverage': 0.30, 'source_reliability': 0.20, 'reconciliation': 0.20, 'causal_validation': 0.15, 'financial_traceability': 0.15}
THRESHOLDS = {'HIGH': 85, 'MEDIUM': 65}
LABELS = {'evidence_coverage': 'Pokrivenost dokazima', 'source_reliability': 'Pouzdanost izvora', 'reconciliation': 'Usklađenost podataka',
          'causal_validation': 'Potvrđenost uzroka', 'financial_traceability': 'Finansijska sljedivost'}


def confidence(components):
    """Ponderisani indeks iz pet komponenti (0–100). Prenesen iz referentnog prototipa v1.2."""
    if any(name not in components or components[name] is None for name in WEIGHTS):
        return {'score': None, 'status': 'INSUFFICIENT_DATA', 'band': 'UNKNOWN'}
    for name in WEIGHTS:
        value = components[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError('Neispravna komponenta pouzdanosti: ' + name)
    score = round(sum(WEIGHTS[name] * components[name] for name in WEIGHTS), 1)
    band = 'HIGH' if score >= THRESHOLDS['HIGH'] else 'MEDIUM' if score >= THRESHOLDS['MEDIUM'] else 'LOW'
    return {'score': score, 'status': 'CALCULATED', 'band': band}


def _share(part, whole):
    return round(100 * part / whole, 1) if whole else None


def build(assess, effects=None, simulated=False):
    """Izvedi pet komponenti iz procjena i finansijskih efekata, s izvornim brojevima i razlogom za svaku."""
    findings = mevan_findings.build(assess, simulated)
    evaluation = mevan_finance_v2.evaluate(effects if isinstance(effects, list) else [], simulated)
    rows = [f for f in findings['findings'] if f['kind'] != 'NIJE_PRIMJENJIVO']
    with_evidence = [f for f in rows if f['kind'] != 'PRAZNINA_U_DOKAZIMA']
    confirmed = [f for f in with_evidence if f['evidence']['status'] == 'POTVRDIO_KONSULTANT' and f['score'] is not None]
    grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    reconciled = {'yes': 0, 'conflict': 0}
    for finding in with_evidence:
        entry = assess.get(finding['code']) if isinstance(assess.get(finding['code']), dict) else {}
        if entry.get('source_grade') in grades:
            grades[entry['source_grade']] += 1
        if entry.get('reconciled') in reconciled:
            reconciled[entry['reconciled']] += 1
    graded, checked = sum(grades.values()), sum(reconciled.values())
    weak = [f for f in rows if f['kind'] == 'KANDIDAT_SLABOST']
    verified_causes = sum(1 for f in weak if f['cause']['status'] == 'POTVRĐEN_UZROK')
    computed = [e for e in evaluation['effects'] if e['amount'] is not None]
    traceable = sum(1 for e in computed if e['state'] == 'POTVRĐEN')
    parts = {
        'evidence_coverage': (_share(len(confirmed), len(rows)), {'potvrđeni_kriteriji': len(confirmed), 'primjenjivi_kriteriji': len(rows)},
                              'Udio primjenjivih kriterija s ocjenom i dokazom koje je potvrdio konsultant.', 'Nema primjenjivih kriterija.'),
        'source_reliability': (_share(grades['A'] + grades['B'], graded), {'A': grades['A'], 'B': grades['B'], 'C': grades['C'], 'D': grades['D'], 'ocijenjeni_izvori': graded},
                               'Udio ocijenjenih izvora razreda A (usaglašeni primarni podaci) ili B (djelimično usaglašeni izvori).',
                               'Nijedan izvor nema razred pouzdanosti (A–D).'),
        'reconciliation': (_share(reconciled['yes'], checked), {'usaglašeno': reconciled['yes'], 'kontradikcija': reconciled['conflict'], 'provjereno': checked},
                           'Udio provjerenih kriterija čiji su izvori usaglašeni; otvorene kontradikcije ga smanjuju.', 'Usklađenost izvora nije provjerena ni za jedan kriterij.'),
        'causal_validation': (_share(verified_causes, len(weak)), {'potvrđeni_uzroci': verified_causes, 'kandidati_za_slabost': len(weak)},
                              'Udio kandidata za slabost čiji je uzrok potvrđen dokazom uz razmotreno konkurentsko objašnjenje.', 'Nema kandidata za slabost s ocjenom i dokazom.'),
        'financial_traceability': (_share(traceable, len(computed)), {'potvrđeni_efekti': traceable, 'izračunati_efekti': len(computed)},
                                   'Udio izračunatih finansijskih efekata koji imaju izvore, dokaz, kontrafaktual, odobrenje i potpun ključ.', 'Nema izračunatih finansijskih efekata.'),
    }
    components = {name: value for name, (value, _, _, _) in parts.items()}
    result = confidence(components)
    return {
        **result, 'provisional': True, 'simulated': bool(simulated),
        'thresholds': dict(THRESHOLDS), 'maturity_index': findings['maturity']['index'],
        'components': [{'id': name, 'label': LABELS[name], 'weight': WEIGHTS[name], 'value': value, 'raw': raw,
                        'rule': rule, 'missing_reason': missing if value is None else ''} for name, (value, raw, rule, missing) in parts.items()],
        'unknown_because': [missing for _, (value, _, _, missing) in parts.items() if value is None],
        'notes': ['Ponderi i pragovi su privremeni i nisu empirijski kalibrisani.', 'Indeks pouzdanosti ne ulazi u indeks zrelosti niti ga mijenja.',
                  'Nedostajući podatak daje NEPOZNATO, ne nulu.'] + (['Podaci su simulacija: indeks opisuje simulaciju, ne stvarnu kompaniju.'] if simulated else []),
    }
