"""Gradi datoteke metodologije iz izvornih materijala. Pokreće se ručno, ne na serveru.

    python methodology/build_from_package.py <folder raspakovanog integracijskog paketa>

v1_61.json nastaje iz kataloga u index.html (današnji model, bez izmjene).
v2_65.json nastaje iz matrice v1.2 i sidrenih opisa ocjena iz integracijskog paketa od 11.11.2026.
Skripta ništa ne dopunjava: polje koje u izvoru ne postoji ostaje prazno.
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MATRIX = '01_METODOLOGIJA_I_65_KRITERIJA/MEVAN_65_Kriterija_Mapiranje_Audit_v1_2.csv'
ANCHORS = '01_METODOLOGIJA_I_65_KRITERIJA/MEVAN_65_KRITERIJA_REVIZIJA_I_SKALE_RADNA.docx'
RULES = '02_PRAVILA_I_TESTOVI/MEVAN_Engine_v1_1_rules.json'
MODULES = (('S', 'Strategija, Uprava i poslovni model'), ('F', 'Finansije i stvaranje vrijednosti'),
           ('O', 'Operacije, proizvodnja i kvalitet'), ('P', 'Planiranje i Supply Chain'),
           ('L', 'Ljudi, organizacija i liderstvo'), ('M', 'Sistem upravljanja i kontinuirano unapređenje'))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def build_v1():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    catalogue = json.loads(re.search(r'const CRITERIA=(\[.*?\]);\n', html, re.S).group(1))
    names = {'F': 'Finansije', 'O': 'Operacije', 'P': 'Planiranje i Supply Chain', 'L': 'Ljudi i liderstvo', 'M': 'Sistem upravljanja'}
    criteria = [{'code': c['code'], 'module': c['code'][0], 'name': c['name'], 'question': c['question'], 'evidence': c['evidence'],
                 'kpi': c['kpi'], 'financial': c['financial'], 'recommendation': c['recommendation']} for c in catalogue]
    write('v1_61.json', {'id': 'v1', 'label': '61 kriterij / 5 modula', 'status': 'active',
                         'modules': [{'code': k, 'name': v} for k, v in names.items()], 'criteria': criteria})


def build_v2(package):
    from docx import Document
    package = Path(package)
    with open(package / MATRIX, encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle, delimiter=';'))
    module_code = {name: code for code, name in MODULES}
    anchors, current = {}, None
    document = Document(str(package / ANCHORS))
    tables = {table._tbl: table for table in document.tables}
    paragraphs = {paragraph._p: paragraph for paragraph in document.paragraphs}
    for block in document.element.body:
        if block in paragraphs:
            match = re.match(r'^([A-Z]\d{2}) — ', paragraphs[block].text.strip())
            if match:
                current = match.group(1)
        elif block in tables and current:
            anchors[current] = {row.cells[0].text.strip(): row.cells[1].text.strip() for row in tables[block].rows}
            current = None
    rules = json.loads((package / RULES).read_text(encoding='utf-8'))
    criteria = []
    for row in rows:
        code = row['ID']
        scale = anchors[code]
        assert list(scale) == ['0', '1', '2', '3', '4', '5'], code
        model = row['Model v1.2']
        criteria.append({
            'code': code, 'module': module_code[row['Modul']], 'name': row['Kriterij'], 'question': row['Dijagnostičko pitanje'],
            'evidence': row['Traženi dokaz'], 'kpi': row['KPI / osnovica'], 'recommendation': row['Preporučena akcija'],
            'owner': row['Vlasnik funkcije'], 'consequence_hypothesis': row['Poslovna posljedica (hipoteza)'],
            'required_check': row['Obavezna provjera'], 'gate': row['Gate'], 'causal_hypothesis_id': row['Uzrocna hipoteza ID'],
            'anchors': [scale[str(level)] for level in range(6)],
            'financial': {'category': row['Finansijska kategorija'], 'model': model, 'family': row['Porodica efekta v1.2'],
                          'status': row['Finansijski status'], 'mapping_reason': row['Razlog mapiranja'],
                          'formula': (rules['financial_models'].get(model) or {}).get('formula', '')},
            'validation': row['Status validacije'],
        })
    write('v2_65.json', {
        'id': 'v2', 'label': '65 kriterija / 6 modula', 'status': 'draft',
        'status_note': 'Nacrt metodologije: svih 65 mapiranja čeka stručnu potvrdu (PENDING_EXPERT_SIGNOFF).',
        'scale': {'unknown': 'NEPOZNATO = nedostaje materijal za ocjenu; nije nula.', 'blocked': 'BLOKIRANO = kontradiktorni ključni izvori.',
                  'not_applicable': 'N/A = obrazložena neprimjenjivost.'},
        'modules': [{'code': code, 'name': name} for code, name in MODULES], 'criteria': criteria,
        'sources': {MATRIX.split('/')[-1]: sha256(package / MATRIX), ANCHORS.split('/')[-1]: sha256(package / ANCHORS), RULES.split('/')[-1]: sha256(package / RULES)},
    })


if __name__ == '__main__':
    build_v1()
    if len(sys.argv) > 1:
        build_v2(sys.argv[1])
