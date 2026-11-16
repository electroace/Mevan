"""Faza 7 integracije 65/6: završni test od početka do kraja kroz API, na tri simulacije iz integracijskog paketa.

Ocjene su iz MEVAN_TRI_KOMPANIJE_65_OCJENA.csv (kolone metal_score_v04, textile_score_v05, wood_score_v10).
Simulacije nose oznaku simulacije, pa u njima ništa ne smije biti potvrđeno. Putanje potvrde (potvrđen uzrok,
potvrđen efekat, razriješeno preklapanje) provjerava zaseban kontrolni slučaj na podacima koji nisu simulacija.
"""
import subprocess

import pytest

import mevan_methodology
import test_project_execution as project_fixture
from test_v2_phase6_premium_pdf import WOOD

METAL='M08:1 S01:2 S02:1 S03:1 S04:2 S05:3 S06:2 S07:2 S08:2 F01:3 F02:2 F03:2 F04:4 F08:2 F09:3 F10:4 F13:2 O01:3 O02:2 O03:2 O05:2 O06:1 O07:0 O08:3 O09:1 O10:1 O11:2 O13:2 O14:3 O15:2 O16:1 P01:2 P02:1 P03:2 P04:1 P05:3 P06:1 P07:2 P08:2 P09:2 P10:2 P11:2 P12:3 P14:1 L01:3 L02:2 L03:3 L04:4 L05:2 L06:3 L07:4 L08:3 L10:2 L11:2 L12:2 M03:2 M04:2 M05:2 M06:3 M07:1 M09:3 M10:1 M11:3 M13:1 M14:2'
TEXTILE='M08:2 S01:2 S02:1 S03:1 S04:2 S05:1 S06:1 S07:3 S08:2 F01:2 F02:1 F03:1 F04:1 F08:2 F09:1 F10:2 F13:1 O01:4 O02:3 O03:2 O05:2 O06:3 O07:3 O08:2 O09:3 O10:2 O11:2 O13:3 O14:3 O15:3 O16:2 P01:2 P02:2 P03:1 P04:2 P05:2 P06:2 P07:2 P08:3 P09:3 P10:2 P11:3 P12:3 P14:1 L01:3 L02:2 L03:3 L04:4 L05:3 L06:2 L07:3 L08:1 L10:1 L11:3 L12:2 M03:3 M04:2 M05:2 M06:3 M07:2 M09:3 M10:2 M11:2 M13:2 M14:2'
COMPANIES={'METALNOVA':(METAL,42.2),'TEKSTILORA':(TEXTILE,43.4),'DRVONOVA':(WOOD,36.6)}
P,C='RECURRING_PNL_KM_YEAR','ONE_TIME_CASH_KM'


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def scores(text):
    return {pair.split(':')[0]:int(pair.split(':')[1]) for pair in text.split()}


def assess(text,**extra):
    return {code:{'score':value,'proof':'confirmed','evidence':'Ogledni dokaz','finding':'Ogledni nalaz',**extra} for code,value in scores(text).items()}


def src(value):
    return {'value':value,'source':'ERP izvod','period':'2026'}


def effects(status='hypothesis',**common):
    base={'key':{'site':'Pogon','period':'2027','account':'6001','item':'Linija 1'},'status':status,**common}
    return [
        {**base,'id':'E1','criterion':'O03','model':'OEE','inputs':{'dodatne_prodane_jedinice_zbog_ogranicenja':src(2000),'kontribucija_po_jedinici':src(55),'dodatni_troskovi':src(10000)},'evidence_ref':'D-1' if common else ''},
        {**base,'id':'E2','criterion':'O07','model':'CHANGEOVER','inputs':{'baseline_min':src(95),'actual_min':src(65),'broj_promjena':src(200),'doprinos_po_min_ogranicenja':src(4),'trosak_implementacije_operativni':src(4000)},'evidence_ref':'D-2' if common else ''},
        {**base,'id':'E3','criterion':'P07','model':'INVENTORY','inputs':{'prosjek_zaliha_baseline':src(850000),'prosjek_zaliha_actual':src(590000),'udio_oslobodivog_kapitala':src(0.75)},
         'key':{'site':'Pogon','period':'2027','account':'1300','item':'Zalihe'},'evidence_ref':'D-3' if common else ''},
        {**base,'id':'E4','criterion':'P10','model':'OTIF','inputs':{'izbjegnuti_penali':src(6000),'izbjegnuti_ekspres_troskovi':src(12096),'dodatna_dokazana_kontribucija':src(0),'dodatni_troskovi':src(2096)},
         'key':{'site':'Pogon','period':'2027','account':'7001','item':'Linija 1'},'evidence_ref':'D-4' if common else ''},
        {**base,'id':'E5','criterion':'S01','model':'OEE','inputs':{}},
    ]


def options():
    option=lambda i,title,values,**k:dict({'id':i,'title':title,'type':'project','criteria':['P02','P03'],'business_case':'Poslovni slučaj.','owner':'Direktor operacija','budget_km':20000,
        'resources':'Planer','kpi':'Pridržavanje plana','steps_30':['Pilot S&OP sastanak'],'steps_90':['Sedmični ritam'],
        'ratings':{f:{'value':v,'rationale':'Procjena na osnovu nalaza.'} for f,v in zip(('profit','liquidity','delivery','risk','feasibility'),values)}},**k)
    return [option('P1','Integrisano planiranje',(5,4,5,4,4)),option('P2','Optimizacija zaliha',(4,5,3,4,3),criteria=['P07']),option('P3','Odgoda nabavke opreme',(2,3,2,3,3),type='defer',criteria=[])]


def post(fx,path,body):
    reply=fx.client.post(path,json=body,headers=fx.headers)
    assert reply.status_code==200,(path,reply.status_code,reply.text[:300])
    return reply


@pytest.mark.parametrize('company',sorted(COMPANIES))
def test_simulated_company_end_to_end(fx,company,tmp_path):
    text,expected_index=COMPANIES[company]
    entered=assess(text)
    # 1) katalog i spremanje dijagnostike 65/6 pored postojeće 61/5
    catalogue=fx.client.get('/api/methodologies/v2').json()
    assert len(catalogue['criteria'])==65 and set(entered)=={c['code'] for c in catalogue['criteria']}
    workspace={'companies':[{'id':'c-'+company,'company':{'name':company+' DEMO'},'diagnostics':[
        {'id':'stara','name':'61/5','assess':{'F05':{'score':3,'proof':'confirmed','evidence':'Dokaz'}},'effects':[]},
        {'id':'nova','name':'65/6','methodology':'v2','report_mode':'demo','assess':entered,'effects_v2':effects(),'options_v2':options()}]}],
        'activeCompanyId':'c-'+company,'activeDiagnosticId':'nova'}
    version=fx.client.get('/api/workspace').json()['version']
    assert fx.client.put('/api/workspace',json=workspace,headers={**fx.headers,'If-Match':version}).status_code==200
    stored=fx.client.get('/api/workspace').json()['workspace']['companies'][0]['diagnostics']
    assert stored[1]['methodology']=='v2' and len(stored[1]['assess'])==65 and 'methodology' not in stored[0]

    # 2) indeks zrelosti: isto pravilo, ručno preračunato iz ocjena
    values=scores(text)
    assert round(sum(values.values())/65*20,1)==expected_index
    findings=post(fx,'/api/v2/findings',{'assess':entered,'simulated':True}).json()
    assert findings['maturity']['index']==expected_index and findings['maturity']['coverage']['confirmed']==65
    for module in catalogue['modules']:
        codes=[c['code'] for c in catalogue['criteria'] if c['module']==module['code']]
        assert findings['maturity']['modules'][module['code']]['index']==round(sum(values[c] for c in codes)/len(codes)*20,1),module['code']

    # 3) nalazi, dokazi i uzroci: simulacija nikad nije potvrđena
    assert len(findings['findings'])==65 and {f['nature'] for f in findings['findings']}=={'SIMULIRANO'}
    assert findings['verified_causes']==0 and all(f['cause']['status']=='HIPOTEZA' and f['consequence']['status']=='HIPOTEZA' for f in findings['findings'])
    weak=sum(1 for value in values.values() if value<=2)
    assert findings['counts'].get('KANDIDAT_SLABOST',0)==weak and findings['counts'].get('PRAZNINA_U_DOKAZIMA',0)==0
    assert sum(findings['counts'].values())==65

    # 4) finansije: formule daju iznose, ali u simulaciji je sve hipotetički potencijal ili blokirano
    finance=post(fx,'/api/v2/finance',{'effects':effects(),'simulated':True}).json()
    assert all(value==0 for value in finance['confirmed'].values()) and finance['grand_total'] is None
    amounts={e['id']:e['amount'] for e in finance['effects']}
    assert amounts=={'E1':100000,'E2':20000,'E3':195000,'E4':16000,'E5':None}
    assert finance['hypothetical_potential'][P]==136000 and finance['hypothetical_potential'][C]==195000
    assert finance['blocked']==[{'id':'E5','reasons':['NEMA_AUTOMATSKE_MONETIZACIJE']}]

    # 5) pouzdanost: odvojena od zrelosti; bez razreda izvora i provjere usklađenosti je nepoznata, ne nula
    confidence=post(fx,'/api/v2/confidence',{'assess':entered,'effects':effects(),'simulated':True}).json()
    assert confidence['score'] is None and confidence['band']=='UNKNOWN' and confidence['maturity_index']==expected_index
    parts={c['id']:c['value'] for c in confidence['components']}
    assert parts['evidence_coverage']==100.0 and parts['source_reliability'] is None and parts['causal_validation']==0.0 and parts['financial_traceability']==0.0

    # 6) rang opcija
    ranking=post(fx,'/api/v2/projects/rank',{'options':options(),'assess':entered,'simulated':True}).json()
    assert ranking['status']=='KONAČAN_RANG' and [(o['id'],o['score']) for o in ranking['options']]==[('P1',90.0),('P2',77.0),('P3',50.0)]  # ručno: 20×(5×.3+4×.2+5×.2+4×.15+4×.15)=90; 20×3,85=77; 20×2,5=50
    assert ranking['has_deferral_option'] and len(ranking['plan_steps']['P1'])==2

    # 7) premium PDF iz istih podataka
    reply=post(fx,'/api/v2/report/premium',{'company':company+' DEMO','diagnostic':'65/6','assess':entered,'effects':effects(),'options':options(),'simulated':True,
                                             'plan':ranking['plan_steps']['P1']})
    path=tmp_path/(company+'.pdf');path.write_bytes(reply.content)
    pages=[p for p in subprocess.check_output(['pdftotext',str(path),'-']).decode().split('\f') if p.strip()]
    whole=' '.join(' '.join(pages).split())
    assert len(pages)>=15 and company+' DEMO' in whole and f'{expected_index:.1f} / 100' in pages[0] and '65 / 65' in pages[0]
    assert all('SIMULACIJA · NACRT METODOLOGIJE 65/6 · NEODOBRENO' in ' '.join(p.split()) for p in pages)
    assert 'Uzrok potvrđen dokazom' not in whole and 'Pilot S&OP sastanak' in whole and 'Svih 65 kriterija' in whole

    # 8) trag u dnevniku
    audit=fx.client.get('/api/audit').text
    for event in ('v2_assessment_changed','v2_findings_built','v2_finance_evaluated','v2_projects_ranked','v2_premium_pdf'):
        assert event in audit,event


def test_control_case_on_real_data_exercises_confirmation_and_overlap_rules(fx):
    """Isti ulazi bez oznake simulacije: ovdje potvrda MORA raditi, a preklapanja se MORAJU blokirati."""
    entered=assess(METAL,source_grade='A',reconciled='yes')
    entered['O07'].update(cause_status='verified',cause_evidence='Mjerenje promjena alata',alternative='Nedostatak alata; isključeno pregledom.')
    findings=post(fx,'/api/v2/findings',{'assess':entered}).json()
    by={f['code']:f for f in findings['findings']}
    assert by['O07']['cause']['status']=='POTVRĐEN_UZROK' and by['O07']['nature']=='POTVRĐENO' and findings['verified_causes']==1
    assert by['O06']['cause']['status']=='HIPOTEZA'

    confirmed=effects('verified',counterfactual='Bez mjere stanje ostaje kao u osnovici.',approved_by='Konsultant')
    finance=post(fx,'/api/v2/finance',{'effects':confirmed}).json()
    states={e['id']:(e['state'],e['reasons']) for e in finance['effects']}
    # E1 (OEE) i E2 (SMED) dijele ključ u istoj porodici; E4 (OTIF) je druga porodica na istoj lokaciji, periodu i nalogu.
    assert states['E2']==('BLOKIRAN',['ISTI_KLJUC_KAO_E1'])
    assert states['E1']==('BLOKIRAN',['MOGUCE_PREKLAPANJE_S_E4']) and states['E4']==('BLOKIRAN',['MOGUCE_PREKLAPANJE_S_E1'])
    assert states['E3']==('POTVRĐEN',[]) and states['E5'][0]=='BLOKIRAN'
    assert finance['confirmed'][P]==0 and finance['confirmed'][C]==195000 and all(v==0 for v in finance['hypothetical_potential'].values())

    resolved=[dict(e) for e in confirmed]
    resolved[3]['independent_of']={'E1':'Penali se odnose na postojećeg kupca, a dodatni kapacitet na novog kupca.'}
    finance=post(fx,'/api/v2/finance',{'effects':resolved}).json()
    assert finance['confirmed'][P]==116000 and finance['confirmed'][C]==195000 and [b['id'] for b in finance['blocked']]==['E2','E5']
    assert finance['grand_total'] is None

    confidence=post(fx,'/api/v2/confidence',{'assess':entered,'effects':resolved}).json()
    assert confidence['status']=='CALCULATED' and confidence['score'] is not None and confidence['maturity_index']==42.2
    weak=sum(1 for value in scores(METAL).values() if value<=2)
    parts={c['id']:c['value'] for c in confidence['components']}
    assert parts=={'evidence_coverage':100.0,'source_reliability':100.0,'reconciliation':100.0,'causal_validation':round(100/weak,1),'financial_traceability':75.0}  # potvrđena 3 (E1, E3, E4) od 4 izračunata efekta
    assert confidence['score']==round(0.30*100+0.20*100+0.20*100+0.15*round(100/weak,1)+0.15*75.0,1)


def test_partial_assessment_keeps_unknown_separate_from_zero_end_to_end(fx):
    entered={code:entry for code,entry in assess(TEXTILE).items() if mevan_methodology.module_of('v2',code) in ('S','F')}
    entered['S01']={'applicable':'no','na_reason':'Kompanija ima jednog kupca po ugovoru.'}
    findings=post(fx,'/api/v2/findings',{'assess':entered}).json()
    modules=findings['maturity']['modules']
    assert findings['maturity']['coverage']=={'criteria':65,'applicable':64,'confirmed':16,'unverified':48,'not_applicable':1}
    assert modules['O']['index'] is None and modules['P']['index'] is None and modules['S']['index'] is not None
    assert findings['counts']['PRAZNINA_U_DOKAZIMA']==48 and findings['counts']['NIJE_PRIMJENJIVO']==1
    pdf=post(fx,'/api/v2/report/premium',{'company':'Djelimična d.o.o.','assess':entered}).content
    assert pdf.startswith(b'%PDF')


def test_metalpro_demo_and_model_61_5_are_unchanged_after_the_whole_integration(fx):
    import json
    from pathlib import Path
    import metalpro_demo
    from project_candidates import prepare_candidates
    analysis=metalpro_demo.analysis()
    assert analysis['index']==36.4 and analysis['coverage']['confirmed']==61 and analysis['independently_verified_criteria']==0
    assert [c['id'] for c in prepare_candidates(analysis)['candidates']][:3]==['C1','C2','C3']
    summary=metalpro_demo.demo_summary()
    assert summary['confirmed_annual_km']==0 and summary['confirmed_one_time_km']==0
    golden=json.loads((Path(metalpro_demo.__file__).parent/'tests'/'golden'/'metalpro_demo.json').read_text(encoding='utf-8'))
    assert golden['server_demo']['index']==36.4 and golden['methodology_61_5']['criteria']==61
    # Stari API za 61/5 radi i kad je model 65/6 uključen.
    ranked=fx.client.post('/api/v4/project-candidates',json={'analysis':analysis},headers=fx.headers)
    assert ranked.status_code==200 and len(ranked.json()['candidates'])>=3
    assert len(mevan_methodology.codes('v1'))==61 and len(mevan_methodology.codes('v2'))==65


def test_stat_boxes_can_shrink_so_long_values_do_not_widen_the_page_on_phones():
    # Greška nađena u završnom browser prolazu: „Nije procijenjeno” je na telefonu širilo stranicu Izvještaji.
    import mevan_nav
    assert '.mv-main .grid>*,.mv-main .stats>*,.mv-main .stat{min-width:0}' in mevan_nav.CSS
    assert '.mv-main .big,.mv-main .number{overflow-wrap:anywhere}' in mevan_nav.CSS
