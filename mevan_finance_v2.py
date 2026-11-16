"""Finansijski modeli i kontrola dvostrukog računanja za model 65/6.

Pravila (specifikacija v1.1/v1.2 i odluka vlasnika od 16.11.2026.):
- Iznos se nikad ne upisuje: računa se iz ulaza formule modela koji katalog propisuje za taj kriterij.
- Kriterij s modelom GENERAL ne može imati novčani efekat.
- Efekat je POTVRĐEN samo ako ima sve ulaze s izvorom i periodom, dokaz, kontrafaktual, odobrenje konsultanta,
  potpun ključ (lokacija, period, konto, proizvod/nalog), pozitivan iznos i ako podaci nisu simulacija.
  Sve ostalo je HIPOTETIČKI POTENCIJAL i nikad se ne dodaje potvrđenom.
- Godišnji P&L, jednokratna gotovina, NPV i očekivana vrijednost rizika su odvojene kolone. Ukupnog zbira nema.
- Isti ključ unutar iste porodice efekta broji se jednom (osim uz zaseban dokaz i potvrđen nepreklapajući obuhvat).
- Dva potvrđena efekta iz različitih porodica koji dijele lokaciju, period i proizvod/nalog blokirani su oba dok
  konsultant pismeno ne obrazloži nezavisnost (uz zaseban dokaz za svaki) ili ne odredi koji se priznaje.
"""
import math

import mevan_methodology

PNL, CASH, NPV, RISK = 'RECURRING_PNL_KM_YEAR', 'ONE_TIME_CASH_KM', 'NPV_KM', 'RISK_EXPECTED_KM_YEAR'
UNITS = (PNL, CASH, NPV, RISK)
KEY_FIELDS = ('site', 'period', 'account', 'item')


def _npv(v):
    flows = v['inkrementalni_novcani_tokovi']
    return sum(flow / (1 + v['diskontna_stopa']) ** year for year, flow in enumerate(flows, 1)) - v['pocetni_capex']


# model: (kolona, ulazi, obračun). Formule su prepisane iz MEVAN_Engine_v1_1_rules.json.
MODELS = {
    'PORTFOLIO': (PNL, ('stara_kontribucija_po_jedinici', 'nova_kontribucija_po_jedinici', 'ostvarena_kolicina', 'dodatni_troskovi'),
                  lambda v: (v['nova_kontribucija_po_jedinici'] - v['stara_kontribucija_po_jedinici']) * v['ostvarena_kolicina'] - v['dodatni_troskovi']),
    'MARGIN': (PNL, ('neto_cijena', 'varijabilni_trosak', 'prodana_kolicina', 'referentna_kontribucija'),
               lambda v: (v['neto_cijena'] - v['varijabilni_trosak']) * v['prodana_kolicina'] - v['referentna_kontribucija']),
    'SCRAP': (PNL, ('skart_baseline_kg', 'skart_actual_kg', 'neto_izbjegnuti_trosak_po_kg', 'dodatni_troskovi'),
              lambda v: (v['skart_baseline_kg'] - v['skart_actual_kg']) * v['neto_izbjegnuti_trosak_po_kg'] - v['dodatni_troskovi']),
    'CHANGEOVER': (PNL, ('baseline_min', 'actual_min', 'broj_promjena', 'doprinos_po_min_ogranicenja', 'trosak_implementacije_operativni'),
                   lambda v: (v['baseline_min'] - v['actual_min']) * v['broj_promjena'] * v['doprinos_po_min_ogranicenja'] - v['trosak_implementacije_operativni']),
    'OEE': (PNL, ('dodatne_prodane_jedinice_zbog_ogranicenja', 'kontribucija_po_jedinici', 'dodatni_troskovi'),
            lambda v: v['dodatne_prodane_jedinice_zbog_ogranicenja'] * v['kontribucija_po_jedinici'] - v['dodatni_troskovi']),
    'INVENTORY': (CASH, ('prosjek_zaliha_baseline', 'prosjek_zaliha_actual', 'udio_oslobodivog_kapitala'),
                  lambda v: (v['prosjek_zaliha_baseline'] - v['prosjek_zaliha_actual']) * v['udio_oslobodivog_kapitala']),
    'INVENTORY_CARRY': (PNL, ('prosjek_smanjenja_zaliha', 'godisnja_stopa_drzanja', 'troskovi_promjene'),
                        lambda v: v['prosjek_smanjenja_zaliha'] * v['godisnja_stopa_drzanja'] - v['troskovi_promjene']),
    'OTIF': (PNL, ('izbjegnuti_penali', 'izbjegnuti_ekspres_troskovi', 'dodatna_dokazana_kontribucija', 'dodatni_troskovi'),
             lambda v: v['izbjegnuti_penali'] + v['izbjegnuti_ekspres_troskovi'] + v['dodatna_dokazana_kontribucija'] - v['dodatni_troskovi']),
    'LABOR': (PNL, ('baseline_sati_po_jedinici', 'actual_sati_po_jedinici', 'ostvarena_kolicina', 'izbjegnuti_trosak_sata'),
              lambda v: (v['baseline_sati_po_jedinici'] - v['actual_sati_po_jedinici']) * v['ostvarena_kolicina'] * v['izbjegnuti_trosak_sata']),
    'DOWNTIME': (PNL, ('izbjegnuti_zastoji_sati', 'vrijednost_sata_ogranicenja', 'dodatni_troskovi'),
                 lambda v: v['izbjegnuti_zastoji_sati'] * v['vrijednost_sata_ogranicenja'] - v['dodatni_troskovi']),
    'QUALITY': (PNL, ('izbjegnuti_trosak_reklamacija', 'izbjegnute_dorade', 'dodatni_troskovi'),
                lambda v: v['izbjegnuti_trosak_reklamacija'] + v['izbjegnute_dorade'] - v['dodatni_troskovi']),
    'CASH': (CASH, ('smanjenje_dso_dana', 'godisnja_kreditna_prodaja'),
             lambda v: v['smanjenje_dso_dana'] * v['godisnja_kreditna_prodaja'] / 365),
    # Očekivana vrijednost rizika nije ostvareni P&L, pa ima vlastitu kolonu.
    'RISK': (RISK, ('promjena_vjerovatnoce_incidenta', 'provjerena_finansijska_posljedica', 'trosak_kontrole'),
             lambda v: v['promjena_vjerovatnoce_incidenta'] * v['provjerena_finansijska_posljedica'] - v['trosak_kontrole']),
    'CAPEX': (NPV, ('inkrementalni_novcani_tokovi', 'diskontna_stopa', 'pocetni_capex'), _npv),
}
FRACTIONS = {'udio_oslobodivog_kapitala', 'godisnja_stopa_drzanja', 'promjena_vjerovatnoce_incidenta', 'diskontna_stopa'}


def allowed_models(criterion_code):
    """Modeli koje katalog dozvoljava za kriterij. Uz INVENTORY ide i godišnji trošak držanja kao zaseban efekat."""
    for criterion in mevan_methodology.load('v2')['criteria']:
        if criterion['code'] == criterion_code:
            model = criterion['financial']['model']
            if model == 'GENERAL':
                return ()
            return (model, 'INVENTORY_CARRY') if model == 'INVENTORY' else (model,)
    return None


def _family(criterion_code):
    return next(c['financial']['family'] for c in mevan_methodology.load('v2')['criteria'] if c['code'] == criterion_code)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return value


def _compute(model, inputs):
    """Vraća (iznos, nedostajući ulazi, ulazi bez izvora ili perioda). Iznos je None ako se ne može izračunati."""
    _, names, formula = MODELS[model]
    values, missing, untraced = {}, [], []
    for name in names:
        item = inputs.get(name) if isinstance(inputs, dict) else None
        item = item if isinstance(item, dict) else {}
        raw = item.get('value')
        if name == 'inkrementalni_novcani_tokovi':
            flows = [_number(x) for x in raw] if isinstance(raw, list) and 1 <= len(raw) <= 40 else [None]
            value = flows if all(x is not None for x in flows) else None
        else:
            value = _number(raw)
            if value is not None and name in FRACTIONS and not 0 <= value <= 1:
                value = None
        if value is None:
            missing.append(name)
        else:
            values[name] = value
        if not str(item.get('source') or '').strip() or not str(item.get('period') or '').strip():
            untraced.append(name)
    if missing:
        return None, missing, untraced
    amount = formula(values)
    return (round(amount, 2) if math.isfinite(amount) else None), missing, untraced


def evaluate(effects, simulated=False):
    """Izračunaj efekte, razdvoji potvrđeno od hipotetičkog i blokiraj svako moguće dvostruko računanje."""
    if not isinstance(effects, list) or len(effects) > 300:
        raise ValueError('Neispravna lista efekata')
    rows = []
    for position, effect in enumerate(effects):
        effect = effect if isinstance(effect, dict) else {}
        row = {'id': str(effect.get('id') or f'efekat-{position + 1}')[:40], 'criterion': str(effect.get('criterion') or '')[:8],
               'model': str(effect.get('model') or '')[:20], 'amount': None, 'unit': None, 'state': 'BLOKIRAN', 'reasons': []}
        rows.append(row)
        models = allowed_models(row['criterion'])
        if models is None:
            row['reasons'].append('NEPOZNAT_KRITERIJ')
            continue
        if not models:
            row['reasons'].append('NEMA_AUTOMATSKE_MONETIZACIJE')
            continue
        if row['model'] not in models:
            row['reasons'].append('MODEL_NIJE_DOZVOLJEN_ZA_KRITERIJ')
            continue
        row['unit'], row['family'] = MODELS[row['model']][0], _family(row['criterion'])
        amount, missing, untraced = _compute(row['model'], effect.get('inputs'))
        row['amount'] = amount
        if missing:
            row['reasons'].append('NEDOSTAJU_ULAZI: ' + ', '.join(missing))
            continue
        if amount is None or amount <= 0:
            row['reasons'].append('IZNOS_NIJE_POZITIVAN')
            continue
        key = effect.get('key') if isinstance(effect.get('key'), dict) else {}
        row['key'] = {field: str(key.get(field) or '').strip()[:80] for field in KEY_FIELDS}
        open_points = []
        if untraced:
            open_points.append('ULAZI_BEZ_IZVORA_ILI_PERIODA: ' + ', '.join(untraced))
        if effect.get('status') != 'verified':
            open_points.append('NIJE_OZNACEN_KAO_POTVRDJEN')
        for field, label in (('evidence_ref', 'NEDOSTAJE_DOKAZ'), ('counterfactual', 'NEDOSTAJE_KONTRAFAKTUAL'), ('approved_by', 'NEDOSTAJE_ODOBRENJE_KONSULTANTA')):
            if not str(effect.get(field) or '').strip():
                open_points.append(label)
        if any(not row['key'][field] for field in KEY_FIELDS):
            open_points.append('NEPOTPUN_KLJUC')
        if simulated:
            open_points.append('PODACI_SU_SIMULACIJA')
        row['state'], row['reasons'] = ('HIPOTEZA', open_points) if open_points else ('KANDIDAT', [])
        row['_effect'] = effect
    candidates = [row for row in rows if row['state'] == 'KANDIDAT']
    # 1) isti ključ unutar iste kolone i porodice
    seen = {}
    for row in candidates:
        full = (row['unit'], row['family']) + tuple(row['key'][field] for field in KEY_FIELDS)
        first = seen.get(full)
        if first is None:
            seen[full] = row
            continue
        effect, other = row['_effect'], first['_effect']
        separate = str(effect.get('incremental_evidence') or '').strip()
        if separate and separate != str(other.get('incremental_evidence') or '').strip() and effect.get('disjoint_scope_verified') is True:
            continue
        row['state'] = 'BLOKIRAN'
        row['reasons'].append('ISTI_KLJUC_KAO_' + first['id'])
    # 2) različite porodice na istoj lokaciji, periodu i proizvodu/nalogu
    candidates = [row for row in candidates if row['state'] == 'KANDIDAT']
    blocked = set()
    for index, row in enumerate(candidates):
        for other in candidates[index + 1:]:
            if row['family'] == other['family'] or any(row['key'][f] != other['key'][f] for f in ('site', 'period', 'item')):
                continue
            first, second = row['_effect'], other['_effect']
            if first.get('yields_to') == other['id']:
                blocked.add((row['id'], 'USTUPLJENO_EFEKTU_' + other['id']))
                continue
            if second.get('yields_to') == row['id']:
                blocked.add((other['id'], 'USTUPLJENO_EFEKTU_' + row['id']))
                continue
            def justified(effect, partner):
                note = effect.get('independent_of') if isinstance(effect.get('independent_of'), dict) else {}
                return len(str(note.get(partner) or '').strip()) >= 20
            distinct_evidence = str(first.get('evidence_ref')).strip() != str(second.get('evidence_ref')).strip()
            if (justified(first, other['id']) or justified(second, row['id'])) and distinct_evidence:
                continue
            blocked.add((row['id'], 'MOGUCE_PREKLAPANJE_S_' + other['id']))
            blocked.add((other['id'], 'MOGUCE_PREKLAPANJE_S_' + row['id']))
    by_id = {row['id']: row for row in candidates}
    for effect_id, reason in sorted(blocked):
        by_id[effect_id]['state'] = 'BLOKIRAN'
        by_id[effect_id]['reasons'].append(reason)
    confirmed, potential = {unit: 0.0 for unit in UNITS}, {unit: 0.0 for unit in UNITS}
    for row in rows:
        row.pop('_effect', None)
        if row['state'] == 'KANDIDAT':
            row['state'] = 'POTVRĐEN'
            confirmed[row['unit']] = round(confirmed[row['unit']] + row['amount'], 2)
        elif row['state'] == 'HIPOTEZA':
            potential[row['unit']] = round(potential[row['unit']] + row['amount'], 2)
    return {'confirmed': confirmed, 'hypothetical_potential': potential, 'grand_total': None, 'simulated': bool(simulated), 'effects': rows,
            'blocked': [{'id': row['id'], 'reasons': row['reasons']} for row in rows if row['state'] == 'BLOKIRAN'],
            'notes': ['Kolone se ne sabiraju međusobno.', 'Hipotetički potencijal nije potvrđena korist i ne dodaje se potvrđenom.',
                      'Blokirani efekti nisu ni u jednoj koloni.']}


def model_catalogue():
    """Opis modela za obrazac unosa: kolona, ulazi i formula iz kataloga metodologije."""
    formulas = {}
    for criterion in mevan_methodology.load('v2')['criteria']:
        formulas.setdefault(criterion['financial']['model'], criterion['financial']['formula'])
    return {name: {'unit': unit, 'inputs': list(inputs), 'formula': formulas.get(name, '')} for name, (unit, inputs, _) in MODELS.items()}
