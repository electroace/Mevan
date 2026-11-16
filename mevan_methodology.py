"""Registar verzija metodologije.

v1 je današnji model (61 kriterij, 5 modula) i ostaje zadan: dijagnostika bez oznake verzije je v1.
v2 je novi model (65 kriterija, 6 modula) iz integracijskog paketa od 11.11.2026. i nosi status „nacrt”
dok vlasnik metodologije ne potvrdi mapiranja. v2 se vidi samo ako je na serveru MEVAN_METHODOLOGY_V2=1;
gašenjem te postavke aplikacija se vraća na ponašanje samo s v1, bez izmjene ijednog podatka.

Podaci su u `methodology/*.json`, a nastaju skriptom `methodology/build_from_package.py`.
Modul kriterija se čita iz kataloga, ne iz prvog slova šifre: u v2 kriterij M08 pripada modulu Strategija.
"""
import json
import math
import os
from functools import lru_cache
from pathlib import Path

DIR = Path(__file__).parent / 'methodology'
FILES = {'v1': 'v1_61.json', 'v2': 'v2_65.json'}
DEFAULT = 'v1'


def v2_enabled():
    return os.getenv('MEVAN_METHODOLOGY_V2', '0') == '1'


def available():
    return ['v1', 'v2'] if v2_enabled() else ['v1']


@lru_cache(maxsize=None)
def load(version):
    """Cijeli katalog jedne verzije. Vraćeni objekat se ne smije mijenjati."""
    if version not in FILES:
        raise KeyError(version)
    return json.loads((DIR / FILES[version]).read_text(encoding='utf-8'))


def version_of(diagnostic):
    """Verzija metodologije dijagnostike; bez oznake (svi dosadašnji podaci) je v1."""
    value = diagnostic.get('methodology') if isinstance(diagnostic, dict) else None
    return value if value in FILES else DEFAULT


def codes(version):
    return [criterion['code'] for criterion in load(version)['criteria']]


def module_of(version, code):
    for criterion in load(version)['criteria']:
        if criterion['code'] == code:
            return criterion['module']
    raise KeyError(code)


def summary(version):
    """Kratak opis verzije za izbor u aplikaciji."""
    data = load(version)
    counts = {}
    for criterion in data['criteria']:
        counts[criterion['module']] = counts.get(criterion['module'], 0) + 1
    return {'id': data['id'], 'label': data['label'], 'status': data['status'], 'status_note': data.get('status_note', ''),
            'criteria': len(data['criteria']),
            'modules': [{'code': m['code'], 'name': m['name'], 'criteria': counts.get(m['code'], 0)} for m in data['modules']]}


def shared_codes():
    """Kriteriji koji postoje u obje verzije pod istom šifrom i istim nazivom (osnova za kopiranje 61/5 → 65/6)."""
    old = {criterion['code']: criterion['name'] for criterion in load('v1')['criteria']}
    return [criterion['code'] for criterion in load('v2')['criteria'] if old.get(criterion['code']) == criterion['name']]


def _score(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if math.isfinite(number) and number.is_integer() and 0 <= number <= 5 else None


def maturity(version, assess):
    """Indeks zrelosti po istom pravilu za svaku verziju: 20 × prosjek potvrđenih primjenjivih ocjena.

    Kriterij se računa samo ako je primjenjiv, označen kao potvrđen, ima cijelu ocjenu 0–5 i tekst dokaza.
    Nepoznato, neprocijenjeno i N/P nisu nula: ne ulaze ni u zbir ni u nazivnik. Bez ijedne potvrđene ocjene indeks je None.
    """
    if not isinstance(assess, dict):
        raise ValueError('Neispravne procjene')
    data = load(version)
    modules = {m['code']: {'name': m['name'], 'applicable': 0, 'verified': 0, 'unverified': 0, 'na': 0, 'sum': 0} for m in data['modules']}
    for criterion in data['criteria']:
        entry = assess.get(criterion['code'])
        entry = entry if isinstance(entry, dict) else {}
        module = modules[criterion['module']]
        if entry.get('applicable') == 'no':
            module['na'] += 1
            continue
        module['applicable'] += 1
        score = _score(entry.get('score'))
        if entry.get('proof') == 'confirmed' and score is not None and str(entry.get('evidence') or '').strip():
            module['verified'] += 1
            module['sum'] += score
        else:
            module['unverified'] += 1
    verified = sum(m['verified'] for m in modules.values())
    total = sum(m['sum'] for m in modules.values())
    for module in modules.values():
        module['index'] = round(20 * module['sum'] / module['verified'], 1) if module['verified'] else None
        del module['sum']
    return {'methodology': version, 'index': round(20 * total / verified, 1) if verified else None,
            'coverage': {'criteria': len(data['criteria']), 'applicable': sum(m['applicable'] for m in modules.values()),
                         'confirmed': verified, 'unverified': sum(m['unverified'] for m in modules.values()),
                         'not_applicable': sum(m['na'] for m in modules.values())},
            'modules': modules}
