"""Rangiranje projektnih opcija za model 65/6 i priprema koraka za plan 90 dana.

Pravila (specifikacija Diagnostic Engine v1, poglavlje 7, i metodologija bodovanja iz paketa od 11.11.2026.):
- Ponderi su verzionisani i vidljivi: profit 30 %, likvidnost 20 %, isporuka/klijent 20 %, upravljivost rizika 15 %,
  izvedivost 15 %. Rezultat = 20 × zbir(ocjena 1–5 × ponder).
- Ocjene daje konsultant, svaku s obrazloženjem. Ocjene su procjena, ne potvrda koristi.
- Rang je konačan tek s najmanje tri potpune opcije; inače je preliminaran. Rang nikad nije odobrenje ulaganja.
- Kriteriji zrelosti nisu projekti: opcija se veže za nalaze, a niska ocjena kriterija ne dokazuje ni uzrok ni korist.
- Opcija je potpuna kad ima poslovni slučaj, vlasnika, budžet, resurse, korake za 30 i 90 dana, KPI i svih pet ocjena.
"""
import mevan_findings
import mevan_methodology

WEIGHTS_VERSION = 'v2-2026-11-11'
WEIGHTS = {'profit': 0.30, 'liquidity': 0.20, 'delivery': 0.20, 'risk': 0.15, 'feasibility': 0.15}
LABELS = {'profit': 'Profit', 'liquidity': 'Likvidnost', 'delivery': 'Isporuka / klijent', 'risk': 'Upravljivost rizika', 'feasibility': 'Izvedivost'}
REQUIRED_TEXT = (('business_case', 'poslovni slučaj'), ('owner', 'vlasnik'), ('resources', 'resursi'), ('kpi', 'KPI'))


def _text(value, limit=2000):
    return str(value or '').strip()[:limit]


def _steps(value):
    return [_text(step, 400) for step in value if _text(step)][:20] if isinstance(value, list) else []


def score(ratings, weights=WEIGHTS):
    """20 × zbir(ocjena × ponder); None ako ijedna ocjena nedostaje ili nije cijeli broj 1–5."""
    total = 0.0
    for factor, weight in weights.items():
        value = (ratings.get(factor) or {}).get('value') if isinstance(ratings.get(factor), dict) else None
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            return None
        total += value * weight
    return round(20 * total, 1)


def _order(rows, weights=WEIGHTS):
    scored = [(score(row['_ratings'], weights), row['id']) for row in rows if score(row['_ratings'], weights) is not None]
    return [item_id for _, item_id in sorted(scored, key=lambda pair: (-pair[0], pair[1]))]


def rank(options, assess, simulated=False):
    """Rangiraj opcije koje je unio konsultant. Ne mijenja ulaz i ništa ne odobrava."""
    if not isinstance(options, list) or len(options) > 30:
        raise ValueError('Neispravna lista opcija')
    findings = {f['code']: f for f in mevan_findings.build(assess if isinstance(assess, dict) else {}, simulated)['findings']}
    known = set(mevan_methodology.codes('v2'))
    rows, seen = [], set()
    for position, option in enumerate(options):
        option = option if isinstance(option, dict) else {}
        option_id = _text(option.get('id'), 40) or f'opcija-{position + 1}'
        if option_id in seen:
            raise ValueError('Duplirana oznaka opcije: ' + option_id)
        seen.add(option_id)
        ratings = option.get('ratings') if isinstance(option.get('ratings'), dict) else {}
        deferral = option.get('type') == 'defer'
        linked = [str(code)[:8] for code in option.get('criteria', []) if isinstance(code, str)][:20] if isinstance(option.get('criteria'), list) else []
        missing = [label for field, label in REQUIRED_TEXT if not _text(option.get(field))]
        budget = option.get('budget_km')
        if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget < 0:
            missing.append('budžet')
        steps_30, steps_90 = _steps(option.get('steps_30')), _steps(option.get('steps_90'))
        if not steps_30:
            missing.append('koraci za 30 dana')
        if not steps_90:
            missing.append('koraci za 90 dana')
        if score(ratings) is None:
            missing.append('svih pet ocjena 1–5')
        if any(not _text((ratings.get(f) or {}).get('rationale') if isinstance(ratings.get(f), dict) else '') for f in WEIGHTS):
            missing.append('obrazloženje svake ocjene')
        notes = []
        unknown = [code for code in linked if code not in known]
        if unknown:
            missing.append('nepostojeći kriteriji: ' + ', '.join(unknown))
        if not linked and not deferral:
            missing.append('veza s najmanje jednim kriterijem')
        not_weak = [code for code in linked if code in findings and findings[code]['kind'] != 'KANDIDAT_SLABOST']
        if not_weak:
            notes.append('Vezani kriteriji koji nisu kandidat za slabost: ' + ', '.join(not_weak) + '. Opcija mora biti obrazložena nalazom, ne samo ocjenom.')
        hypotheses = [code for code in linked if code in findings and findings[code]['cause']['status'] != 'POTVRĐEN_UZROK']
        if hypotheses:
            notes.append('Uzrok je još hipoteza za: ' + ', '.join(hypotheses) + '.')
        rows.append({'id': option_id, 'title': _text(option.get('title'), 200) or option_id, 'type': 'defer' if deferral else 'project',
                     'criteria': linked, 'score': score(ratings), 'complete': not missing, 'missing': missing, 'notes': notes,
                     'owner': _text(option.get('owner'), 200), 'kpi': _text(option.get('kpi'), 400), 'budget_km': budget if 'budžet' not in missing else None,
                     'steps_30': steps_30, 'steps_90': steps_90, '_ratings': ratings})
    order = _order(rows)
    position = {option_id: index + 1 for index, option_id in enumerate(order)}
    complete = [row for row in rows if row['complete']]
    # Osjetljivost: da li se prvi izbor mijenja kad se jednom faktoru doda 10 procentnih poena (ostali se srazmjerno smanje).
    changes = []
    if order:
        for factor in WEIGHTS:
            shifted = {name: (weight + 0.10 if name == factor else weight) for name, weight in WEIGHTS.items()}
            total = sum(shifted.values())
            alternative = _order(rows, {name: weight / total for name, weight in shifted.items()})
            if alternative and alternative[0] != order[0]:
                changes.append({'factor': factor, 'label': LABELS[factor], 'first_becomes': alternative[0]})
    for row in rows:
        row['rank'] = position.get(row['id'])
        row.pop('_ratings')
    rows.sort(key=lambda row: (row['rank'] is None, row['rank'] or 0, row['id']))
    final = len(complete) >= 3
    return {
        'weights_version': WEIGHTS_VERSION, 'weights': dict(WEIGHTS), 'formula': '20 × zbir(ocjena 1–5 × ponder)',
        'status': 'KONAČAN_RANG' if final else 'PRELIMINARAN_RANG',
        'status_reason': '' if final else f'Potrebne su najmanje tri potpune opcije; potpunih je {len(complete)}.',
        'has_deferral_option': any(row['type'] == 'defer' for row in rows), 'simulated': bool(simulated),
        'options': rows, 'first': order[0] if order else None,
        'sensitivity': {'stable': not changes, 'first_changes_when_weight_rises': changes},
        'notes': ['Rang nije odobrenje ulaganja ni potvrda koristi.', 'Ocjene su procjena konsultanta.',
                  'Kriteriji zrelosti nisu projekti: niska ocjena otvara pitanje, ne dokazuje uzrok ni finansijsku korist.']
                 + ([] if any(row['type'] == 'defer' for row in rows) else ['Nije unesena opcija odgode ili neinvestiranja; razmotriti je kad je relevantna.'])
                 + (['Podaci su simulacija.'] if simulated else []),
    }


def plan_steps(option):
    """Koraci jedne rangirane opcije u obliku stavki plana 90 dana. Rokovi se ne izmišljaju: ostaju prazni."""
    items = []
    for period, steps in (('1–30 dana', option.get('steps_30', [])), ('31–90 dana', option.get('steps_90', []))):
        for step in steps:
            items.append({'task': f'[{period}] {step}', 'owner': option.get('owner', ''), 'due': '', 'kpi': option.get('kpi', ''),
                          'status': 'Nije počelo', 'source_option': option.get('id', '')})
    return items
