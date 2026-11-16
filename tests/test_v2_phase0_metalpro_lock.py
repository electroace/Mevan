"""Faza 0 integracije 65/6: zaključavanje METALPRO DEMO stanja.

Ovaj test ne provjerava novu funkcionalnost. Čuva otisak postojećeg modela 61/5 i METALPRO DEMO
(ocjene, indeks 36,4, 0 KM potvrđenih efekata, kandidati C1–C3, struktura Word izvještaja), tako da
svaka kasnija faza odmah pokaže ako ih je nešto pomjerilo.

Otisak je u tests/golden/metalpro_demo.json. Mijenja se samo svjesno, uz odobrenje:
    python tests/test_v2_phase0_metalpro_lock.py --write
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
GOLDEN=ROOT/'tests'/'golden'/'metalpro_demo.json'
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))


def _digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()


def methodology_fingerprint():
    """Model 61/5 kakav je danas u aplikaciji (server i preglednik)."""
    from diagnostic_engine import CODES,DIMENSIONS
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    catalogue=json.loads(re.search(r'const CRITERIA=(\[.*?\]);\n',html,re.S).group(1))
    return {
        'criteria':len(CODES),'dimensions':DIMENSIONS,
        'per_dimension':{d:sum(1 for c in CODES if c.startswith(d)) for d in DIMENSIONS},
        'codes_sha256':_digest(sorted(CODES)),
        'browser_catalogue_codes_sha256':_digest(sorted(c['code'] for c in catalogue)),
        'browser_catalogue_text_sha256':_digest([[c['code'],c['dim'],c['name'],c['question'],c['evidence'],c['kpi'],c['financial'],c['recommendation']] for c in catalogue]),
    }


def server_demo_fingerprint():
    """METALPRO DEMO na serveru: ocjene, indeks, kandidati, rangiranje, nacrt projekta i finansijski scenariji."""
    import metalpro_demo as demo
    from project_candidates import prepare_candidates
    from project_planner import rank
    analysis=demo.analysis()
    candidates=prepare_candidates(analysis)['candidates']
    ranked=rank(analysis,demo.candidate_ratings(analysis))['candidates']
    summary=demo.demo_summary()
    return {
        'index':analysis['index'],'coverage':analysis['coverage'],'dimensions':analysis['dimensions'],
        'independently_verified_criteria':analysis['independently_verified_criteria'],
        'weak_criteria':analysis['weak_criteria'],'critical':analysis['critical'],
        'causal_hypotheses':[{k:h[k] for k in ('title','criteria','status')} for h in analysis['causal_hypotheses']],
        'priority_decisions':[{k:d[k] for k in ('title','criteria','status')} for d in analysis['priority_decisions']],
        'candidates':[{k:c[k] for k in ('id','title','criterion_codes','hypothesis_status','financial_impact','priority')} for c in candidates],
        'ranking':[{'id':c['id'],'score':c['score']} for c in ranked],
        'proposed_project':summary['proposed_project'],'project_status':summary['project_status'],
        'confirmed_annual_km':summary['confirmed_annual_km'],'confirmed_one_time_km':summary['confirmed_one_time_km'],
        'independently_verified_financial_km':summary['independently_verified_financial_km'],
        'financial_scenarios':[{k:s[k] for k in ('name','annual_gross_benefit_km','annual_net_benefit_km','one_time_working_capital_release_km','confirmed_annual_benefit_km','confirmed_one_time_benefit_km','status')} for s in summary['financial_scenarios']],
    }


def word_report_fingerprint():
    """METALPRO DEMO u pregledniku, kroz ukupni detaljni Word izvještaj: struktura, ocjene i finansijska tabela."""
    from docx import Document
    with tempfile.TemporaryDirectory() as folder:
        subprocess.run(['node','qa_word_reports.js'],cwd=ROOT,env={**os.environ,'MEVAN_WORD_QA_DIR':folder},check=True,capture_output=True,timeout=120)
        document=Document(str(Path(folder)/'MEVAN_UKUPNO_Detaljni.docx'))
    paragraphs=[p.text.strip() for p in document.paragraphs if p.text.strip()]
    criteria=[]
    for text in paragraphs:
        match=re.match(r'^([FOPLM]\d{2})\s+·\s+(.+?)\s+\|\s+(\d)/5$',text)
        if match:
            criteria.append([match.group(1),match.group(2),int(match.group(3))])
    tables=[[[cell.text.strip() for cell in row.cells] for row in table.rows] for table in document.tables]
    scores=[score for _,_,score in criteria]
    return {
        'sections':[t for t in paragraphs if re.match(r'^0\d\s+\|\s+',t)],
        'criteria_count':len(criteria),'criteria_sha256':_digest(criteria),
        'index_from_scores':round(sum(scores)/len(scores)*20,1) if scores else None,
        'overview_table':tables[0],'dimension_table':tables[1],'finance_table':next(t for t in tables if t[0][0]=='Kategorija'),
        'table_count':len(tables),
    }


def fingerprint():
    return {'methodology_61_5':methodology_fingerprint(),'server_demo':server_demo_fingerprint(),'word_report':word_report_fingerprint()}


def _golden():
    return json.loads(GOLDEN.read_text(encoding='utf-8'))


def test_methodology_61_5_is_unchanged():
    assert methodology_fingerprint()==_golden()['methodology_61_5']


def test_server_metalpro_demo_is_unchanged():
    current=server_demo_fingerprint()
    assert current==_golden()['server_demo']
    # Vrijednosti koje su izričito zaštićene zahtjevom integracije.
    assert current['index']==36.4 and current['coverage']['confirmed']==61
    assert current['confirmed_annual_km']==0 and current['confirmed_one_time_km']==0
    assert [c['id'] for c in current['candidates']][:3]==['C1','C2','C3']


def test_browser_metalpro_demo_word_report_is_unchanged():
    current=word_report_fingerprint()
    assert current==_golden()['word_report']
    assert current['criteria_count']==61 and current['index_from_scores']==36.4


if __name__=='__main__':
    if sys.argv[1:]==['--write']:
        GOLDEN.parent.mkdir(parents=True,exist_ok=True)
        GOLDEN.write_text(json.dumps(fingerprint(),ensure_ascii=False,indent=1,sort_keys=True)+'\n',encoding='utf-8')
        print('Upisan otisak:',GOLDEN)
    else:
        print(json.dumps(fingerprint(),ensure_ascii=False,indent=1,sort_keys=True))
