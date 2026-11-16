"""Faza 4 integracije 65/6: indeks pouzdanosti nalaza, odvojen od indeksa zrelosti.

Prvih pet testova su scenariji referentnog prototipa paketa (build_mevan_v12.py), preneseni na stvarni kod.
"""
from pathlib import Path

import pytest

import mevan_confidence as conf
import mevan_methodology
import test_project_execution as project_fixture
from test_v2_phase3_finance import effect

ALL={'evidence_coverage':100,'source_reliability':100,'reconciliation':100,'causal_validation':100,'financial_traceability':100}


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def test_weights_and_thresholds_are_the_provisional_ones_from_the_specification():
    assert conf.WEIGHTS=={'evidence_coverage':0.30,'source_reliability':0.20,'reconciliation':0.20,'causal_validation':0.15,'financial_traceability':0.15}
    assert sum(conf.WEIGHTS.values())==pytest.approx(1.0) and conf.THRESHOLDS=={'HIGH':85,'MEDIUM':65}


def test_missing_component_gives_unknown_never_zero():
    for name in conf.WEIGHTS:
        partial=dict(ALL);partial[name]=None
        assert conf.confidence(partial)=={'score':None,'status':'INSUFFICIENT_DATA','band':'UNKNOWN'}
        del partial[name]
        assert conf.confidence(partial)['score'] is None


def test_weighted_sum_and_bands():
    assert conf.confidence(ALL)=={'score':100.0,'status':'CALCULATED','band':'HIGH'}
    assert conf.confidence({**ALL,'evidence_coverage':0})['score']==70.0
    assert conf.confidence({'evidence_coverage':90,'source_reliability':80,'reconciliation':70,'causal_validation':60,'financial_traceability':50})['score']==73.5
    assert [conf.confidence({k:v for k in conf.WEIGHTS})['band'] for v in (85,84.9,65,64.9,0)]==['HIGH','MEDIUM','MEDIUM','LOW','LOW']


@pytest.mark.parametrize('bad',[-1,101,'90',True,float('nan')])
def test_invalid_component_values_are_rejected(bad):
    with pytest.raises(ValueError):
        conf.confidence({**ALL,'reconciliation':bad})


def test_confidence_never_changes_the_maturity_index():
    assess={'O03':{'score':1,'proof':'confirmed','evidence':'Dnevnik'},'O05':{'score':5,'proof':'confirmed','evidence':'Evidencija'}}
    before=mevan_methodology.maturity('v2',assess)
    graded={code:{**entry,'source_grade':'D','reconciled':'conflict'} for code,entry in assess.items()}
    result=conf.build(graded,[])
    assert result['maturity_index']==before['index']==60.0
    assert mevan_methodology.maturity('v2',graded)['index']==60.0


def test_empty_diagnostic_is_unknown_with_a_reason_for_every_missing_component():
    result=conf.build({},[])
    assert result['score'] is None and result['band']=='UNKNOWN' and result['provisional'] is True
    values={c['id']:c['value'] for c in result['components']}
    # Pokrivenost je poznata i iznosi 0 (65 primjenjivih, 0 potvrđenih); ostale četiri nemaju podatke.
    assert values=={'evidence_coverage':0.0,'source_reliability':None,'reconciliation':None,'causal_validation':None,'financial_traceability':None}
    assert len(result['unknown_because'])==4 and all(c['missing_reason'] for c in result['components'] if c['value'] is None)


def full_case():
    entry=lambda score,**more:{'score':score,'proof':'confirmed','evidence':'Dokaz','finding':'Nalaz',**more}
    assess={
        'O03':entry(1,source_grade='A',reconciled='yes',cause_status='verified',cause_evidence='Pareto',alternative='Materijal; isključeno.'),
        'O05':entry(2,source_grade='C',reconciled='conflict'),
        'O07':entry(4,source_grade='B',reconciled='yes'),
        'P07':{'score':3,'proof':'review','evidence':'Stanje zaliha','source_grade':'D'},
    }
    effects=[effect('A',model='OEE'),effect('B',model='INVENTORY',status='hypothesis',key={'item':'SKU-1'})]
    return assess,effects


def test_components_are_derived_from_entered_data_with_raw_values():
    assess,effects=full_case()
    result=conf.build(assess,effects)
    by={c['id']:c for c in result['components']}
    assert by['evidence_coverage']['raw']=={'potvrđeni_kriteriji':3,'primjenjivi_kriteriji':65} and by['evidence_coverage']['value']==4.6
    assert by['source_reliability']['raw']=={'A':1,'B':1,'C':1,'D':1,'ocijenjeni_izvori':4} and by['source_reliability']['value']==50.0
    assert by['reconciliation']['raw']=={'usaglašeno':2,'kontradikcija':1,'provjereno':3} and by['reconciliation']['value']==66.7
    assert by['causal_validation']['raw']=={'potvrđeni_uzroci':1,'kandidati_za_slabost':2} and by['causal_validation']['value']==50.0
    assert by['financial_traceability']['raw']=={'potvrđeni_efekti':1,'izračunati_efekti':2} and by['financial_traceability']['value']==50.0
    expected=round(0.30*4.6+0.20*50.0+0.20*66.7+0.15*50.0+0.15*50.0,1)
    assert result['score']==expected==39.7 and result['band']=='LOW' and result['status']=='CALCULATED'
    assert all(c['rule'] and c['weight']==conf.WEIGHTS[c['id']] for c in result['components'])


def test_not_applicable_criteria_are_left_out_of_coverage():
    result=conf.build({'S01':{'applicable':'no','na_reason':'Nije primjenjivo u ovom obuhvatu.'}},[])
    assert next(c for c in result['components'] if c['id']=='evidence_coverage')['raw']=={'potvrđeni_kriteriji':0,'primjenjivi_kriteriji':64}


def test_simulated_data_is_marked_and_cannot_have_verified_causes_or_confirmed_effects():
    assess,effects=full_case()
    result=conf.build(assess,effects,simulated=True)
    by={c['id']:c['value'] for c in result['components']}
    assert result['simulated'] is True and by['causal_validation']==0.0 and by['financial_traceability']==0.0
    assert any('simulacija' in note for note in result['notes'])


def test_api_is_protected_and_follows_the_server_setting(fx,monkeypatch):
    assess,effects=full_case()
    ok=fx.client.post('/api/v2/confidence',json={'assess':assess,'effects':effects},headers=fx.headers)
    assert ok.status_code==200 and ok.json()['score']==39.7 and ok.json()['provisional'] is True
    assert fx.client.post('/api/v2/confidence',json={'assess':assess},headers={'Origin':'https://evil.example'}).status_code==403
    assert fx.client.post('/api/v2/confidence',json={'assess':'x'},headers=fx.headers).status_code==400
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','0')
    assert fx.client.post('/api/v2/confidence',json={'assess':assess},headers=fx.headers).status_code==404
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.post('/api/v2/confidence',json={'assess':assess},headers=fx.headers).status_code==401


def test_page_shows_confidence_separately_with_raw_values_and_the_provisional_note():
    html=(Path(conf.__file__).parent/'index.html').read_text(encoding='utf-8')
    assert html.count('data-field="source_grade"')==1 and html.count('data-field="reconciled"')==1
    panel=html[html.index('function confidencePanel(c){'):html.index('// Lanac nalaza (model 65/6)')] if html.index('function confidencePanel(c){')<html.index('// Lanac nalaza (model 65/6)') else html[html.index('function confidencePanel(c){'):html.index('function confidencePanel(c){')+2600]
    for text in ('Indeks pouzdanosti','Indeks zrelosti (odvojeno)','Nedostajući podatak nije nula.','Izvorne vrijednosti','su privremeni i nisu empirijski kalibrisani','Pouzdanost ne mijenja indeks zrelosti.'):
        assert text in panel,text
    assert "fetch('/api/v2/confidence'," in html and '${confidencePanel(v2Confidence)}${groups}' in html
