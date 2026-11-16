"""Faza 1a integracije 65/6: registar verzija metodologije (bez promjene sučelja i bez promjene v1)."""
import json
from pathlib import Path

import pytest

import mevan_methodology as registry
import test_project_execution as project_fixture

ROOT=Path(registry.__file__).parent


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.delenv('MEVAN_METHODOLOGY_V2',raising=False)
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def test_v1_is_exactly_the_model_the_app_uses_today():
    import re
    from diagnostic_engine import CODES,DIMENSIONS
    v1=registry.load('v1')
    assert v1['status']=='active' and set(registry.codes('v1'))==CODES and len(registry.codes('v1'))==61
    assert [m['code'] for m in v1['modules']]==list(DIMENSIONS)
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    browser=json.loads(re.search(r'const CRITERIA=(\[.*?\]);\n',html,re.S).group(1))
    fields=('code','name','question','evidence','kpi','financial','recommendation')
    assert [[c[f] for f in fields] for c in browser]==[[c[f] for f in fields] for c in v1['criteria']]
    assert all(c['module']==c['code'][0] for c in v1['criteria'])


def test_v2_structure_matches_the_integration_package():
    v2=registry.load('v2')
    assert v2['status']=='draft' and 'PENDING_EXPERT_SIGNOFF' in v2['status_note']
    criteria=v2['criteria']
    assert len(criteria)==65 and len({c['code'] for c in criteria})==65
    assert {m['code']:m['criteria'] for m in registry.summary('v2')['modules']}=={'S':9,'F':8,'O':14,'P':13,'L':11,'M':10}
    # M08 zadržava šifru, ali pripada modulu Strategija: modul se ne smije izvoditi iz prvog slova.
    assert registry.module_of('v2','M08')=='S'
    assert [c['code'] for c in criteria if c['code'][0]!=c['module']]==['M08']
    for criterion in criteria:
        assert len(criterion['anchors'])==6 and all(text.strip() for text in criterion['anchors']),criterion['code']
        assert criterion['validation']=='PENDING_EXPERT_SIGNOFF'
        for field in ('name','question','evidence','kpi','recommendation','owner','consequence_hypothesis','gate'):
            assert criterion[field].strip(),(criterion['code'],field)
    status={}
    for criterion in criteria:
        status[criterion['financial']['status']]=status.get(criterion['financial']['status'],0)+1
    assert status=={'NO_AUTO_VALUE':45,'CONDITIONAL_EVIDENCE_REQUIRED':20}
    # Model GENERAL nikad nema obračun: umjesto formule nosi izričitu zabranu automatske monetizacije.
    for criterion in criteria:
        general=criterion['financial']['model']=='GENERAL'
        assert general==(criterion['financial']['status']=='NO_AUTO_VALUE'),criterion['code']
        assert criterion['financial']['formula'].startswith('NEMA_AUTOMATSKE_MONETIZACIJE')==general,criterion['code']


def test_difference_between_versions_is_exactly_as_analysed():
    old,new=set(registry.codes('v1')),set(registry.codes('v2'))
    assert sorted(new-old)==['F13','L11','L12','M13','M14','O16','P14','S01','S02','S03','S04','S05','S06','S07','S08']
    assert sorted(old-new)==['F05','F06','F07','F11','F12','L09','M01','M02','M12','O04','O12']
    shared=registry.shared_codes()
    assert len(shared)==50 and set(shared)==old&new


def test_maturity_rule_reproduces_the_locked_metalpro_index_for_v1():
    import metalpro_demo
    from diagnostic_engine import CODES
    assess={}
    for dim,total in metalpro_demo.DIMENSION_SUMS.items():
        group=sorted(c for c in CODES if c.startswith(dim))
        base,extra=divmod(total,len(group))
        for position,code in enumerate(group):
            assess[code]={'score':base+(position<extra),'proof':'confirmed','evidence':'SIMULIRANO'}
    result=registry.maturity('v1',assess)
    engine=metalpro_demo.analysis()
    assert result['index']==engine['index']==36.4
    assert {k:v['index'] for k,v in result['modules'].items()}=={k:v['index'] for k,v in engine['dimensions'].items()}
    assert result['coverage']['confirmed']==61


def test_unknown_and_not_applicable_are_never_zero_in_v2():
    empty=registry.maturity('v2',{})
    assert empty['index'] is None and empty['coverage']=={'criteria':65,'applicable':65,'confirmed':0,'unverified':65,'not_applicable':0}
    assess={'S01':{'score':4,'proof':'confirmed','evidence':'Dokaz'},'M08':{'score':2,'proof':'confirmed','evidence':'Dokaz'},
            'S02':{'score':5,'proof':'unverified','evidence':'Dokaz'},'S03':{'score':5,'proof':'confirmed','evidence':''},
            'F01':{'applicable':'no'},'F02':{'score':'nije broj','proof':'confirmed','evidence':'Dokaz'}}
    result=registry.maturity('v2',assess)
    # Računaju se samo S01 i M08 (oba u modulu Strategija): (4+2)/2 × 20 = 60.
    assert result['index']==60.0 and result['modules']['S']['index']==60.0 and result['modules']['S']['verified']==2
    assert result['modules']['F']['index'] is None and result['modules']['F']['na']==1
    assert result['modules']['M']['index'] is None and result['modules']['M']['verified']==0


def test_existing_data_without_a_version_mark_is_v1():
    assert registry.version_of({})=='v1' and registry.version_of({'methodology':'v2'})=='v2'
    assert registry.version_of({'methodology':'nepoznato'})=='v1' and registry.version_of(None)=='v1'


def test_api_hides_v2_until_the_server_setting_is_on(fx,monkeypatch):
    listing=fx.client.get('/api/methodologies').json()
    assert listing['default']=='v1' and [v['id'] for v in listing['versions']]==['v1']
    assert fx.client.get('/api/methodologies/v1').json()['criteria'][0]['code']=='F01'
    assert fx.client.get('/api/methodologies/v2').status_code==404
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    listing=fx.client.get('/api/methodologies').json()
    assert [(v['id'],v['status'],v['criteria']) for v in listing['versions']]==[('v1','active',61),('v2','draft',65)]
    assert len(fx.client.get('/api/methodologies/v2').json()['criteria'])==65
    assert fx.client.get('/api/methodologies/v3').status_code==404
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.get('/api/methodologies').status_code==401 and fx.client.get('/api/methodologies/v1').status_code==401


def test_methodology_data_is_shipped_with_the_container():
    assert 'COPY --chown=mevan:mevan methodology ./methodology' in (ROOT/'Dockerfile').read_text(encoding='utf-8')
    assert (ROOT/'methodology'/'v1_61.json').is_file() and (ROOT/'methodology'/'v2_65.json').is_file()


# ---- faza 1b: stranica prati metodologiju aktivne dijagnostike

def test_page_keeps_v1_catalogue_embedded_and_swaps_content_for_v2():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    # Ugrađeni katalog v1 i njegove liste ostaju iste; mijenja se samo njihov sadržaj.
    assert html.count('const CRITERIA=[')==1 and 'const DIMS=[...new Set(CRITERIA.map(c=>c.dim))];' in html
    assert "const METHOD={active:'v1',booted:false,missing:false,v1:{criteria:CRITERIA.map(c=>c),dims:[...DIMS]},v2:null};" in html
    assert "function methodologyOf(diagnostic){return diagnostic&&diagnostic.methodology==='v2'?'v2':'v1'}" in html
    assert 'CRITERIA.length=0;CRITERIA.push(...METHOD[use].criteria);' in html and 'DIMS.length=0;DIMS.push(...METHOD[use].dims);' in html
    assert 'approved:d.approved};applyMethodology(d);};' in html


def test_new_v1_diagnostic_gets_no_version_mark_and_v2_is_explicit():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert "...(methodology==='v2'?{methodology:'v2'}:{})});" in html
    assert "async function addDiagnostic(methodology='v1'){if(methodology==='v2'&&!METHOD.v2)return mvNotify(" in html
    # Dugme za 65/6 postoji samo kad je katalog stigao sa servera.
    assert "${METHOD.v2?'<button class=\"btn secondary\" onclick=\"addDiagnostic(\\'v2\\')\">+ Nova dijagnostika 65/6 (nacrt)</button>':''}" in html


def test_counts_follow_the_active_model_instead_of_fixed_61_and_5():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert '${s.valid}/61<' not in html and '.length}/5<' not in html
    assert '<div class="big">${s.valid}/${CRITERIA.length}</div>' in html and '.done).length}/${DIMS.length}</div>' in html
    assert "${validCount}/${x.methodology==='v2'?65:61} potvrđenih" in html


def test_v2_shows_criterion_anchors_and_blocks_unfinished_screens():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert "(c.anchors?c.anchors.map((text,level)=>level+' — '+text):SCORE_GUIDE)" in html
    assert "const V2_BLOCKED_PAGES=['v2'];" in html  # od faze 1c zatvorena je samo integrisana AI analiza
    assert "else if(METHOD.active==='v2'&&V2_BLOCKED_PAGES.includes(page)){" in html
    assert "if(METHOD.missing&&!['workspace','data'].includes(page)){" in html
    assert "if(methodologyOf(diagnostic)==='v2')return mvNotify('Vođeno prikupljanje još nije dostupno za model 65/6.',true);" in html
    assert 'Model 65/6 je nacrt metodologije: mapiranja kriterija čekaju stručnu potvrdu.' in html


def test_catalogue_v2_is_loaded_from_the_server_before_first_render():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    boot=html[html.index('async function cloudBoot(){'):html.index("page=hashPage()||page;render();")]
    assert "fetch('/api/methodologies')" in boot and "fetch('/api/methodologies/v2')" in boot and 'METHOD.booted=true;syncState();' in boot


def test_workspace_with_a_v2_diagnostic_round_trips_through_the_server(fx):
    workspace={'companies':[{'id':'c1','company':{'name':'QA'},'diagnostics':[
        {'id':'d1','name':'Stara','assess':{'F05':{'score':3,'proof':'confirmed','evidence':'Dokaz'}},'effects':[]},
        {'id':'d2','name':'Nova 65/6','methodology':'v2','assess':{'S01':{'score':4,'proof':'confirmed','evidence':'Dokaz'}},'effects':[]}]}],
        'activeCompanyId':'c1','activeDiagnosticId':'d2'}
    version=fx.client.get('/api/workspace').json()['version']
    assert fx.client.put('/api/workspace',json=workspace,headers={**fx.headers,'If-Match':version}).status_code==200
    stored=fx.client.get('/api/workspace').json()['workspace']['companies'][0]['diagnostics']
    assert 'methodology' not in stored[0] and stored[1]['methodology']=='v2' and stored[1]['assess']['S01']['score']==4
    assert registry.maturity(registry.version_of(stored[1]),stored[1]['assess'])['index']==80.0
    assert registry.maturity(registry.version_of(stored[0]),stored[0]['assess'])['index']==60.0


# ---- faza 1c: izvještaji i analiza po pravilima za 65/6, kopiranje 61/5 → 65/6

def test_v2_reports_carry_the_draft_methodology_notice_and_ai_stays_closed():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert "const V2_DRAFT_NOTICE='MODEL 65/6 — NACRT METODOLOGIJE: mapiranja kriterija čekaju stručnu potvrdu. Nije za klijenta.';" in html
    assert "if(METHOD.active==='v2')add(V2_DRAFT_NOTICE,'Notice');" in html
    # Oznaka mora biti u samom pregledu za štampu, odmah ispod dugmeta, ne negdje drugdje u stranici.
    assert "Štampaj / sačuvaj PDF</button>${METHOD.active==='v2'?'<p><em>'+esc(V2_DRAFT_NOTICE)+'</em></p>':''}${body}</body></html>" in html
    assert "async function makeAIDraft(dim){if(METHOD.active==='v2')return mvNotify('AI nacrt još nije dostupan za model 65/6." in html


def test_copy_to_v2_creates_a_new_unverified_diagnostic_and_never_edits_the_source():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    copy=html[html.index('async function copyToV2(){'):html.index('async function addCompany(){')]
    assert "if(methodologyOf(source)!=='v1'||!METHOD.v2)return mvNotify(" in copy
    assert "const shared=METHOD.v2.criteria.filter(c=>oldNames[c.code]===c.name).map(c=>c.code);" in copy
    assert "const target=makeAssessment(source.name+' — kopija 65/6','v2');" in copy
    # Kopira se vrijednost, ne veza, i status dokaza se vraća na „nije provjereno”.
    assert "const entry=JSON.parse(JSON.stringify(source.assess[code]));entry.proof='none';target.assess[code]=entry" in copy
    assert 'source.assess[code]=' not in copy and 'delete source' not in copy and 'await mvConfirm(text,' in copy
    assert "${METHOD.v2&&methodologyOf(d)==='v1'?'<button class=\"btn secondary\" onclick=\"copyToV2()\">Kopiraj u novu dijagnostiku 65/6</button>':''}" in html


def test_shared_criteria_used_for_copy_are_the_same_fifty_on_server_and_in_browser():
    v1={c['code']:c['name'] for c in registry.load('v1')['criteria']}
    browser_rule=[c['code'] for c in registry.load('v2')['criteria'] if v1.get(c['code'])==c['name']]
    assert browser_rule==registry.shared_codes() and len(browser_rule)==50
