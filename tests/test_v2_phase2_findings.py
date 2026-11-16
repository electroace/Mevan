"""Faza 2 integracije 65/6: lanac nalaza i revizijski dnevnik."""
from pathlib import Path

import pytest

import mevan_findings
import test_project_execution as project_fixture

ROOT=Path(mevan_findings.__file__).parent
FULL={'score':1,'proof':'confirmed','evidence':'Dnevnik zastoja 2026-01 do 2026-10','finding':'Zastoji se ne evidentiraju po uzroku.'}


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def one(assess,code,simulated=False):
    result=mevan_findings.build(assess,simulated)
    return next(f for f in result['findings'] if f['code']==code),result


def test_every_criterion_gets_a_complete_chain_from_the_catalogue():
    result=mevan_findings.build({})
    assert len(result['findings'])==65 and result['methodology_status']=='draft'
    for finding in result['findings']:
        for key in ('code','module','name','kind','nature','evidence','claim','cause','consequence','recommendation','owner_role','kpi','required_check','gate','financial'):
            assert key in finding,(finding['code'],key)
        assert finding['consequence']['status']=='HIPOTEZA' and finding['cause']['id'].startswith('HYP-')
        assert finding['financial']['amount'] is None  # u ovoj fazi se ništa ne računa u novcu


def test_unknown_score_is_an_evidence_gap_not_a_weakness_and_not_zero():
    finding,result=one({},'O03')
    assert finding['kind']=='PRAZNINA_U_DOKAZIMA' and finding['score'] is None and finding['first_step'].startswith('Pribaviti: ')
    assert result['counts']=={'PRAZNINA_U_DOKAZIMA':65} and result['maturity']['index'] is None
    # Ocjena bez teksta dokaza je i dalje praznina, čak i kad je niska.
    assert one({'O03':{'score':0,'proof':'confirmed','evidence':''}},'O03')[0]['kind']=='PRAZNINA_U_DOKAZIMA'


def test_classification_follows_the_specification():
    kinds={}
    for score,proof in ((0,'confirmed'),(2,'none'),(3,'confirmed'),(4,'review'),(5,'confirmed')):
        kinds[(score,proof)]=one({'O03':{'score':score,'proof':proof,'evidence':'Dokaz'}},'O03')[0]['kind']
    assert kinds=={(0,'confirmed'):'KANDIDAT_SLABOST',(2,'none'):'KANDIDAT_SLABOST',(3,'confirmed'):'DJELIMICNO_RAZVIJENO',
                   (4,'review'):'NEPOTVRDJENA_SNAGA',(5,'confirmed'):'KANDIDAT_SNAGA'}
    na=one({'O03':{'applicable':'no','na_reason':'Proces ne postoji u ovom pogonu.'}},'O03')[0]
    assert na['kind']=='NIJE_PRIMJENJIVO' and na['not_applicable_reason']=='Proces ne postoji u ovom pogonu.'
    assert one({'O03':{'score':2,'proof':'confirmed','evidence':'Dokaz'}},'O03')[0]['level_description'].startswith('Postoje parcijalni zapisi')


def test_low_score_never_proves_a_cause_by_itself():
    finding,_=one({'O03':dict(FULL)},'O03')
    assert finding['kind']=='KANDIDAT_SLABOST' and finding['cause']['status']=='HIPOTEZA'
    assert finding['cause']['not_verified_because']==['konsultant nije označio uzrok kao potvrđen','nije naveden dokaz uzroka','nije razmotreno konkurentsko objašnjenje']
    assert finding['publication']=={'ready':False,'missing':['konkurentsko objašnjenje']}


@pytest.mark.parametrize('missing',['cause_status','cause_evidence','alternative','proof'])
def test_cause_is_verified_only_when_every_condition_holds(missing):
    entry={**FULL,'cause_status':'verified','cause_evidence':'Pareto zastoja po uzroku','alternative':'Nedostatak materijala; isključeno uvidom u zalihe.'}
    assert one({'O03':dict(entry)},'O03')[0]['cause']['status']=='POTVRĐEN_UZROK'
    broken=dict(entry)
    broken[missing]='none' if missing=='proof' else ''
    assert one({'O03':broken},'O03')[0]['cause']['status']=='HIPOTEZA'


def test_simulated_data_is_never_presented_as_confirmed_or_as_a_verified_cause():
    entry={**FULL,'cause_status':'verified','cause_evidence':'Pareto','alternative':'Materijal'}
    finding,result=one({'O03':entry},'O03',simulated=True)
    assert finding['nature']=='SIMULIRANO' and finding['cause']['status']=='HIPOTEZA' and 'podaci su simulacija' in finding['cause']['not_verified_because']
    assert result['simulated'] is True and result['verified_causes']==0
    assert {f['nature'] for f in result['findings']}=={'SIMULIRANO'}
    real=mevan_findings.build({'O03':entry,'O05':{'score':2,'proof':'none','evidence':'Dokaz'}})
    assert {f['code']:f['nature'] for f in real['findings'] if f['code'] in ('O03','O05')}=={'O03':'POTVRĐENO','O05':'NEPOTVRĐENO'}


def test_logic_gate_lists_weak_candidates_that_are_not_ready_for_publication():
    ready={**FULL,'alternative':'Materijal'}
    result=mevan_findings.build({'O03':ready,'O05':dict(FULL)})
    assert result['gate_logic_check']=={'ready':False,'not_ready':['O05']}
    assert mevan_findings.build({'O03':ready})['gate_logic_check']=={'ready':True,'not_ready':[]}
    assert mevan_findings.build({})['gate_logic_check']['ready'] is False  # bez kandidata nema šta da prođe


def test_api_requires_login_origin_and_the_server_setting(fx,monkeypatch):
    body={'assess':{'O03':dict(FULL)},'simulated':False}
    ok=fx.client.post('/api/v2/findings',json=body,headers=fx.headers)
    assert ok.status_code==200 and ok.json()['counts']['KANDIDAT_SLABOST']==1
    assert 'v2_findings_built' in fx.client.get('/api/audit').text
    assert fx.client.post('/api/v2/findings',json=body,headers={'Origin':'https://evil.example'}).status_code==403
    assert fx.client.post('/api/v2/findings',json={'assess':'nije objekat'},headers=fx.headers).status_code==400
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','0')
    assert fx.client.post('/api/v2/findings',json=body,headers=fx.headers).status_code==404
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.post('/api/v2/findings',json=body,headers=fx.headers).status_code==401


def test_audit_records_field_changes_for_v2_only_and_never_the_evidence_text():
    def workspace(entry,methodology='v2'):
        diagnostic={'id':'d1','assess':{'O03':entry}}
        if methodology:diagnostic['methodology']=methodology
        return {'companies':[{'id':'c1','diagnostics':[diagnostic]}]}
    before=workspace({'score':2,'proof':'none','evidence':'TAJNI TEKST DOKAZA'})
    after=workspace({'score':3,'proof':'confirmed','evidence':'DRUGI TAJNI TEKST','cause_status':'verified'})
    changes=mevan_findings.assessment_changes(before,after)
    assert changes==[{'diagnostic':'d1','criterion':'O03','changes':{'score':[2,3],'proof':['none','confirmed'],'cause_status':[None,'verified']}}]
    assert 'TAJNI' not in str(changes)
    assert mevan_findings.assessment_changes(after,after)==[]
    # Dijagnostike 61/5 se ne prate ovim dnevnikom; njihovo ponašanje ostaje kao prije.
    assert mevan_findings.assessment_changes(workspace({'score':1},None),workspace({'score':5},None))==[]
    assert mevan_findings.assessment_changes(None,after)[0]['changes']['score']==[None,3]


def test_saving_the_workspace_writes_the_audit_trail(fx):
    def put(entry):
        version=fx.client.get('/api/workspace').json()['version']
        body={'companies':[{'id':'c1','company':{},'diagnostics':[{'id':'d2','methodology':'v2','assess':{'S01':entry},'effects':[]}]}],'activeCompanyId':'c1','activeDiagnosticId':'d2'}
        assert fx.client.put('/api/workspace',json=body,headers={**fx.headers,'If-Match':version}).status_code==200
    put({'score':2,'proof':'none','evidence':'Povjerljiv dokaz'})
    put({'score':4,'proof':'confirmed','evidence':'Povjerljiv dokaz'})
    audit=fx.client.get('/api/audit').text
    assert audit.count('v2_assessment_changed')==2 and 'Povjerljiv dokaz' not in audit


def test_page_has_cause_fields_only_for_v2_and_a_findings_screen():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert html.count('data-field="alternative"')==1 and html.count('data-field="cause_status"')==1 and html.count('data-field="cause_evidence"')==1
    card=html[html.index('data-field="finding">${esc(a.finding)}</textarea>'):html.index('<label>Finansijski efekat (opis i pretpostavke)</label>')]
    assert card.startswith('data-field="finding">${esc(a.finding)}</textarea>${c.anchors?`') and card.endswith('`:""}')
    assert "else if(page==='findings'){html=findingsPage()}" in html and "fetch('/api/v2/findings'," in html
    assert "'findings'];" in html[html.index('const NAV_PAGES='):html.index('const NAV_PAGES=')+140]
