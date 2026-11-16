"""Faza 5 integracije 65/6: rangiranje projektnih opcija i koraci za plan 90 dana."""
from pathlib import Path

import pytest

import mevan_projects_v2 as projects
import test_project_execution as project_fixture

WEAK={'score':1,'proof':'confirmed','evidence':'Dokaz','finding':'Nalaz'}
ASSESS={'P02':dict(WEAK),'P03':dict(WEAK),'O05':{**WEAK,'score':2},'L01':{**WEAK,'score':4}}


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def option(option_id,values=(3,3,3,3,3),**changes):
    data={'id':option_id,'title':'Opcija '+option_id,'type':'project','criteria':['P02'],
          'ratings':{factor:{'value':value,'rationale':'Procjena na osnovu nalaza.'} for factor,value in zip(projects.WEIGHTS,values)},
          'business_case':'Stabilizacija plana smanjuje hitne promjene.','owner':'Direktor operacija','budget_km':15000,'resources':'Planer, 2 dana sedmično',
          'kpi':'Pridržavanje plana %','steps_30':['Pilot S&OP sastanak','Mapa narudžbi'],'steps_90':['Sedmični ritam','Pregled rezultata']}
    data.update(changes)
    return data


def test_weights_are_versioned_and_match_the_package():
    assert projects.WEIGHTS=={'profit':0.30,'liquidity':0.20,'delivery':0.20,'risk':0.15,'feasibility':0.15}
    assert sum(projects.WEIGHTS.values())==pytest.approx(1.0) and projects.WEIGHTS_VERSION=='v2-2026-11-11'
    # Model 61/5 zadržava svoje pondere.
    import project_planner
    assert project_planner.WEIGHTS=={'profit':25,'liquidity':20,'delivery':25,'risk':20,'feasibility':10}


def test_score_formula_is_20_times_weighted_sum():
    rate=lambda *values:{f:{'value':v,'rationale':'x'} for f,v in zip(projects.WEIGHTS,values)}
    assert projects.score(rate(5,5,5,5,5))==100.0 and projects.score(rate(1,1,1,1,1))==20.0
    assert projects.score(rate(5,4,3,2,1))==round(20*(5*.30+4*.20+3*.20+2*.15+1*.15),1)==67.0
    for bad in (0,6,2.5,'3',True,None):
        assert projects.score(rate(bad,3,3,3,3)) is None,bad
    assert projects.score({}) is None


def test_ranking_orders_by_score_and_is_final_only_with_three_complete_options():
    two=projects.rank([option('A',(5,4,3,2,1)),option('B',(2,2,2,2,2))],ASSESS)
    assert two['status']=='PRELIMINARAN_RANG' and 'potpunih je 2' in two['status_reason']
    assert [(o['id'],o['rank'],o['score']) for o in two['options']]==[('A',1,67.0),('B',2,40.0)]
    three=projects.rank([option('B',(2,2,2,2,2)),option('A',(5,4,3,2,1)),option('C',(4,4,4,4,4),type='defer',criteria=[])],ASSESS)
    assert three['status']=='KONAČAN_RANG' and three['first']=='C' and [o['id'] for o in three['options']]==['C','A','B']
    assert three['has_deferral_option'] is True and 'Rang nije odobrenje ulaganja ni potvrda koristi.' in three['notes']
    assert any('odgode ili neinvestiranja' in note for note in two['notes'])


@pytest.mark.parametrize('change,missing',[
    ({'business_case':''},'poslovni slučaj'),({'owner':' '},'vlasnik'),({'resources':''},'resursi'),({'kpi':''},'KPI'),
    ({'budget_km':None},'budžet'),({'budget_km':-5},'budžet'),({'steps_30':[]},'koraci za 30 dana'),({'steps_90':['  ']},'koraci za 90 dana'),
    ({'criteria':[]},'veza s najmanje jednim kriterijem'),({'criteria':['ZZ9']},'nepostojeći kriteriji: ZZ9')])
def test_incomplete_option_is_listed_with_what_is_missing_and_does_not_count_towards_three(change,missing):
    result=projects.rank([option('A',**change),option('B'),option('C')],ASSESS)
    first=next(o for o in result['options'] if o['id']=='A')
    assert first['complete'] is False and missing in first['missing']
    assert result['status']=='PRELIMINARAN_RANG'


def test_missing_rating_or_rationale_keeps_option_unranked_or_incomplete():
    no_rating=option('A');del no_rating['ratings']['risk']
    no_reason=option('B');no_reason['ratings']['profit']['rationale']=''
    result=projects.rank([no_rating,no_reason,option('C')],ASSESS)
    by={o['id']:o for o in result['options']}
    assert by['A']['score'] is None and by['A']['rank'] is None and 'svih pet ocjena 1–5' in by['A']['missing']
    assert by['B']['score']==60.0 and by['B']['complete'] is False and 'obrazloženje svake ocjene' in by['B']['missing']


def test_options_are_tied_to_findings_not_to_scores_alone():
    result=projects.rank([option('A',criteria=['P02','L01','S01'])],ASSESS)
    notes=' '.join(result['options'][0]['notes'])
    # L01 ima ocjenu 4, S01 nema ocjenu: nijedan nije kandidat za slabost.
    assert 'nisu kandidat za slabost: L01, S01' in notes and 'Uzrok je još hipoteza za: P02, L01, S01' in notes


def test_sensitivity_reports_when_the_first_choice_depends_on_the_weights():
    close=projects.rank([option('A',(4,3,3,3,3)),option('B',(3,3,3,5,3))],ASSESS)
    assert close['first']=='A' and close['sensitivity']['stable'] is False
    assert {'factor':'risk','label':'Upravljivost rizika','first_becomes':'B'} in close['sensitivity']['first_changes_when_weight_rises']
    clear=projects.rank([option('A',(5,5,5,5,5)),option('B',(1,1,1,1,1))],ASSESS)
    assert clear['sensitivity']=={'stable':True,'first_changes_when_weight_rises':[]}


def test_plan_steps_carry_owner_and_kpi_and_never_invent_dates():
    result=projects.rank([option('A')],ASSESS)
    steps=projects.plan_steps(result['options'][0])
    assert [s['task'] for s in steps]==['[1–30 dana] Pilot S&OP sastanak','[1–30 dana] Mapa narudžbi','[31–90 dana] Sedmični ritam','[31–90 dana] Pregled rezultata']
    assert all(s['owner']=='Direktor operacija' and s['kpi']=='Pridržavanje plana %' and s['due']=='' and s['status']=='Nije počelo' and s['source_option']=='A' for s in steps)


def test_invalid_input_and_duplicate_ids_are_rejected():
    with pytest.raises(ValueError):
        projects.rank('x',{})
    with pytest.raises(ValueError,match='Duplirana'):
        projects.rank([option('A'),option('A')],ASSESS)


def test_api_is_protected_logged_and_returns_plan_steps(fx,monkeypatch):
    body={'options':[option('A',(5,4,3,2,1)),option('B'),option('C',type='defer',criteria=[])],'assess':ASSESS}
    ok=fx.client.post('/api/v2/projects/rank',json=body,headers=fx.headers)
    assert ok.status_code==200 and ok.json()['status']=='KONAČAN_RANG' and ok.json()['first']=='A' and len(ok.json()['plan_steps']['A'])==4
    assert 'v2_projects_ranked' in fx.client.get('/api/audit').text
    assert fx.client.post('/api/v2/projects/rank',json={'options':[option('A'),option('A')]},headers=fx.headers).status_code==400
    assert fx.client.post('/api/v2/projects/rank',json=body,headers={'Origin':'https://evil.example'}).status_code==403
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','0')
    assert fx.client.post('/api/v2/projects/rank',json=body,headers=fx.headers).status_code==404
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.post('/api/v2/projects/rank',json=body,headers=fx.headers).status_code==401


def test_options_screen_ranks_on_the_server_and_adds_plan_steps_only_after_confirmation():
    html=(Path(projects.__file__).parent/'index.html').read_text(encoding='utf-8')
    assert "else if(page==='options'){html=optionsV2Page()}" in html and "'options'];" in html[html.index('const NAV_PAGES='):html.index('const NAV_PAGES=')+150]
    page=html[html.index('let v2Ranking=null'):html.index('// Finansijski efekti za model 65/6.')]
    assert "fetch('/api/v2/projects/rank',{method:'POST'" in page and 'row.score' in page
    transfer=page[page.index('async function optionToPlanV2(id){'):page.index('function optionsV2Page(){')]
    assert transfer.index('await mvConfirm(')<transfer.index('state.plan.push(') and 'state.plan=' not in transfer and 'splice' not in transfer
    assert 'Rang nije odobrenje ulaganja ni potvrda koristi.' in page and page.count('v2Ranking=null')>=4
    assert "document.querySelectorAll('[data-opt2]').forEach(el=>el.onchange=()=>setOpt2(el));" in html
