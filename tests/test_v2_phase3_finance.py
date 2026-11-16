"""Faza 3a integracije 65/6: finansijski modeli i kontrola dvostrukog računanja (server).

Scenariji iz referentnog prototipa paketa (build_mevan_v12.py) preneseni su ovdje na stvarni engine;
testovi indeksa pouzdanosti iz istog prototipa dolaze s fazom 4.
"""
import pytest

import mevan_finance_v2 as finance
import mevan_methodology
import test_project_execution as project_fixture

P,C,N,R=finance.PNL,finance.CASH,finance.NPV,finance.RISK


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def src(value):
    return {'value':value,'source':'ERP izvod','period':'2026'}


INPUTS={
    'PORTFOLIO':({'stara_kontribucija_po_jedinici':10,'nova_kontribucija_po_jedinici':14,'ostvarena_kolicina':1000,'dodatni_troskovi':500},3500),
    'MARGIN':({'neto_cijena':50,'varijabilni_trosak':30,'prodana_kolicina':1000,'referentna_kontribucija':15000},5000),
    'SCRAP':({'skart_baseline_kg':1000,'skart_actual_kg':600,'neto_izbjegnuti_trosak_po_kg':5,'dodatni_troskovi':500},1500),
    'CHANGEOVER':({'baseline_min':95,'actual_min':65,'broj_promjena':200,'doprinos_po_min_ogranicenja':4,'trosak_implementacije_operativni':4000},20000),
    'OEE':({'dodatne_prodane_jedinice_zbog_ogranicenja':2000,'kontribucija_po_jedinici':55,'dodatni_troskovi':10000},100000),
    'INVENTORY':({'prosjek_zaliha_baseline':850000,'prosjek_zaliha_actual':590000,'udio_oslobodivog_kapitala':0.75},195000),
    'INVENTORY_CARRY':({'prosjek_smanjenja_zaliha':1300000,'godisnja_stopa_drzanja':0.12,'troskovi_promjene':0},156000),
    'OTIF':({'izbjegnuti_penali':6000,'izbjegnuti_ekspres_troskovi':12096,'dodatna_dokazana_kontribucija':0,'dodatni_troskovi':2096},16000),
    'LABOR':({'baseline_sati_po_jedinici':0.5,'actual_sati_po_jedinici':0.4,'ostvarena_kolicina':10000,'izbjegnuti_trosak_sata':12},12000),
    'DOWNTIME':({'izbjegnuti_zastoji_sati':96,'vrijednost_sata_ogranicenja':150,'dodatni_troskovi':672},13728),
    'QUALITY':({'izbjegnuti_trosak_reklamacija':7000,'izbjegnute_dorade':3000,'dodatni_troskovi':1000},9000),
    'CASH':({'smanjenje_dso_dana':10,'godisnja_kreditna_prodaja':3650000},100000),
    'RISK':({'promjena_vjerovatnoce_incidenta':0.1,'provjerena_finansijska_posljedica':200000,'trosak_kontrole':5000},15000),
    'CAPEX':({'inkrementalni_novcani_tokovi':[110,121],'diskontna_stopa':0.1,'pocetni_capex':150},50),
}
CRITERION={'PORTFOLIO':'S02','MARGIN':'F02','SCRAP':'O05','CHANGEOVER':'O07','OEE':'O03','INVENTORY':'P07','INVENTORY_CARRY':'P07','OTIF':'P10',
           'LABOR':'O01','DOWNTIME':'O10','CASH':'F13','RISK':'M08','CAPEX':'S06'}


def effect(effect_id='A',model='SCRAP',criterion=None,key=None,**changes):
    data={'id':effect_id,'criterion':criterion or CRITERION[model],'model':model,'inputs':{k:src(v) for k,v in INPUTS[model][0].items()},
          'key':{'site':'Zenica','period':'2027','account':'6001','item':'NALOG-1',**(key or {})},
          'status':'verified','evidence_ref':'Dokaz-'+effect_id,'counterfactual':'Bez mjere stanje ostaje kao u osnovici.','approved_by':'Konsultant'}
    data.update(changes)
    return data


def states(result):
    return {row['id']:row['state'] for row in result['effects']}


def test_every_criterion_maps_to_a_known_model_and_general_has_none():
    with_model=0
    for criterion in mevan_methodology.load('v2')['criteria']:
        models=finance.allowed_models(criterion['code'])
        if criterion['financial']['model']=='GENERAL':
            assert models==(),criterion['code']
        else:
            assert models and all(m in finance.MODELS for m in models),criterion['code']
            with_model+=1
    assert with_model==20 and finance.allowed_models('P07')==('INVENTORY','INVENTORY_CARRY')


@pytest.mark.parametrize('model',sorted(CRITERION))
def test_each_formula_computes_the_expected_amount_in_its_own_column(model):
    result=finance.evaluate([effect(model=model)])
    row=result['effects'][0]
    assert row['state']=='POTVRĐEN' and row['amount']==pytest.approx(INPUTS[model][1]),row
    expected_unit={'INVENTORY':C,'CASH':C,'CAPEX':N,'RISK':R}.get(model,P)
    assert row['unit']==expected_unit and result['confirmed'][expected_unit]==pytest.approx(INPUTS[model][1])
    assert sum(result['confirmed'].values())==pytest.approx(INPUTS[model][1]) and result['grand_total'] is None


def test_quality_formula_exists_even_though_no_criterion_uses_it_yet():
    amount,missing,_=finance._compute('QUALITY',{k:src(v) for k,v in INPUTS['QUALITY'][0].items()})
    assert amount==INPUTS['QUALITY'][1] and not missing


def test_general_criteria_and_wrong_models_never_produce_money():
    result=finance.evaluate([effect('G',criterion='S01'),effect('W',model='OEE',criterion='O05'),effect('X',criterion='ZZ9')])
    assert states(result)=={'G':'BLOKIRAN','W':'BLOKIRAN','X':'BLOKIRAN'}
    assert [b['reasons'] for b in result['blocked']]==[['NEMA_AUTOMATSKE_MONETIZACIJE'],['MODEL_NIJE_DOZVOLJEN_ZA_KRITERIJ'],['NEPOZNAT_KRITERIJ']]
    assert all(value==0 for value in list(result['confirmed'].values())+list(result['hypothetical_potential'].values()))


def test_amount_is_calculated_from_inputs_never_taken_from_a_typed_total():
    typed=effect(amount=999999)
    assert finance.evaluate([typed])['effects'][0]['amount']==1500
    broken=effect()
    del broken['inputs']['skart_actual_kg']
    row=finance.evaluate([broken])['effects'][0]
    assert row['state']=='BLOKIRAN' and row['amount'] is None and row['reasons']==['NEDOSTAJU_ULAZI: skart_actual_kg']
    for bad in ('abc',None,True,float('nan'),float('inf')):
        wrong=effect()
        wrong['inputs']['skart_actual_kg']['value']=bad
        assert finance.evaluate([wrong])['effects'][0]['state']=='BLOKIRAN',bad
    fraction=effect(model='INVENTORY')
    fraction['inputs']['udio_oslobodivog_kapitala']['value']=75
    assert 'NEDOSTAJU_ULAZI: udio_oslobodivog_kapitala' in finance.evaluate([fraction])['effects'][0]['reasons']
    loss=effect()
    loss['inputs']['dodatni_troskovi']['value']=5000
    assert finance.evaluate([loss])['effects'][0]['reasons']==['IZNOS_NIJE_POZITIVAN']


@pytest.mark.parametrize('change,reason',[
    ({'status':'hypothesis'},'NIJE_OZNACEN_KAO_POTVRDJEN'),({'evidence_ref':''},'NEDOSTAJE_DOKAZ'),({'counterfactual':' '},'NEDOSTAJE_KONTRAFAKTUAL'),
    ({'approved_by':''},'NEDOSTAJE_ODOBRENJE_KONSULTANTA'),({'key':{'site':'Zenica','period':'2027','account':'','item':'NALOG-1'}},'NEPOTPUN_KLJUC')])
def test_one_missing_requirement_keeps_the_effect_hypothetical(change,reason):
    result=finance.evaluate([effect(**change)])
    row=result['effects'][0]
    assert row['state']=='HIPOTEZA' and row['reasons']==[reason]
    assert result['confirmed'][P]==0 and result['hypothetical_potential'][P]==1500


def test_input_without_source_or_period_cannot_be_confirmed():
    untraced=effect()
    untraced['inputs']['skart_baseline_kg']['source']=''
    row=finance.evaluate([untraced])['effects'][0]
    assert row['state']=='HIPOTEZA' and row['reasons']==['ULAZI_BEZ_IZVORA_ILI_PERIODA: skart_baseline_kg']


def test_simulated_data_is_never_confirmed():
    result=finance.evaluate([effect(),effect('B',model='INVENTORY')],simulated=True)
    assert states(result)=={'A':'HIPOTEZA','B':'HIPOTEZA'} and all(value==0 for value in result['confirmed'].values())
    assert result['hypothetical_potential'][P]==1500 and result['hypothetical_potential'][C]==195000


def test_cash_release_and_annual_saving_stay_in_separate_columns():
    # Primjer iz specifikacije: 195.000 KM oslobođene gotovine i 156.000 KM/god nisu 351.000 KM profita.
    result=finance.evaluate([effect('zalihe',model='INVENTORY'),effect('drzanje',model='INVENTORY_CARRY')])
    assert result['confirmed'][C]==195000 and result['confirmed'][P]==156000 and result['grand_total'] is None
    assert 351000 not in result['confirmed'].values()


def test_confirmed_and_hypothetical_are_never_added_together():
    result=finance.evaluate([effect('A'),effect('B',key={'item':'NALOG-2'},status='hypothesis')])
    assert result['confirmed'][P]==1500 and result['hypothetical_potential'][P]==1500


def test_same_key_in_the_same_family_counts_once():
    # Primjer iz specifikacije: OEE i SMED na istoj mašini, kontu, periodu i nalogu su isti novac.
    result=finance.evaluate([effect('oee',model='OEE'),effect('smed',model='CHANGEOVER')])
    assert states(result)=={'oee':'POTVRĐEN','smed':'BLOKIRAN'} and result['confirmed'][P]==100000
    assert result['blocked']==[{'id':'smed','reasons':['ISTI_KLJUC_KAO_oee']}]


def test_incremental_effect_needs_separate_evidence_and_verified_disjoint_scope():
    base=effect('oee',model='OEE',incremental_evidence='E-1')
    assert states(finance.evaluate([base,effect('smed',model='CHANGEOVER',incremental_evidence='E-1',disjoint_scope_verified=True)]))['smed']=='BLOKIRAN'
    assert states(finance.evaluate([base,effect('smed',model='CHANGEOVER',incremental_evidence='E-2')]))['smed']=='BLOKIRAN'
    result=finance.evaluate([base,effect('smed',model='CHANGEOVER',incremental_evidence='E-2',disjoint_scope_verified=True)])
    assert states(result)=={'oee':'POTVRĐEN','smed':'POTVRĐEN'} and result['confirmed'][P]==120000


def test_different_period_or_account_is_a_different_key():
    assert finance.evaluate([effect('a',model='OEE'),effect('b',model='CHANGEOVER',key={'period':'2028'})])['confirmed'][P]==120000
    assert finance.evaluate([effect('a',model='OEE'),effect('b',model='CHANGEOVER',key={'account':'6002'})])['confirmed'][P]==120000


def test_different_families_sharing_site_period_and_item_are_both_blocked_until_resolved():
    oee,otif=effect('oee',model='OEE'),effect('otif',model='OTIF',key={'account':'7001'})
    result=finance.evaluate([oee,otif])
    assert states(result)=={'oee':'BLOKIRAN','otif':'BLOKIRAN'} and result['confirmed'][P]==0
    assert {b['id']:b['reasons'] for b in result['blocked']}=={'oee':['MOGUCE_PREKLAPANJE_S_otif'],'otif':['MOGUCE_PREKLAPANJE_S_oee']}
    # Različit proizvod/nalog, lokacija ili period nije preklapanje.
    assert finance.evaluate([oee,effect('otif',model='OTIF',key={'item':'NALOG-9'})])['confirmed'][P]==116000


def test_cross_family_overlap_is_resolved_only_by_written_justification_with_separate_evidence_or_by_yielding():
    oee=effect('oee',model='OEE',independent_of={'otif':'Kapacitet je prodat novom kupcu; penali se odnose na postojećeg kupca.'})
    otif=effect('otif',model='OTIF')
    assert finance.evaluate([oee,otif])['confirmed'][P]==116000
    short=effect('oee',model='OEE',independent_of={'otif':'nezavisno'})
    assert finance.evaluate([short,otif])['confirmed'][P]==0
    same_evidence=effect('otif',model='OTIF',evidence_ref='Dokaz-oee')
    assert finance.evaluate([oee,same_evidence])['confirmed'][P]==0
    result=finance.evaluate([effect('oee',model='OEE'),effect('otif',model='OTIF',yields_to='oee')])
    assert states(result)=={'oee':'POTVRĐEN','otif':'BLOKIRAN'} and result['confirmed'][P]==100000
    assert result['blocked']==[{'id':'otif','reasons':['USTUPLJENO_EFEKTU_oee']}]


def test_npv_and_risk_are_not_added_to_profit_or_cash():
    result=finance.evaluate([effect('p'),effect('n',model='CAPEX',key={'item':'INV-1'}),effect('r',model='RISK',key={'item':'RIZIK-1'})])
    assert result['confirmed']=={P:1500,C:0,N:pytest.approx(50),R:15000}


def test_invalid_input_shape_is_rejected():
    with pytest.raises(ValueError):
        finance.evaluate('nije lista')
    assert finance.evaluate([None,'tekst'])['effects'][0]['state']=='BLOKIRAN'


def test_api_is_protected_logged_and_stores_nothing(fx,monkeypatch):
    body={'effects':[effect()],'simulated':False}
    ok=fx.client.post('/api/v2/finance',json=body,headers=fx.headers)
    assert ok.status_code==200 and ok.json()['confirmed'][P]==1500
    models=fx.client.get('/api/v2/finance/models').json()
    assert models['criteria']['P07']==['INVENTORY','INVENTORY_CARRY'] and 'S01' not in models['criteria'] and len(models['criteria'])==20
    assert models['models']['SCRAP']['inputs']==['skart_baseline_kg','skart_actual_kg','neto_izbjegnuti_trosak_po_kg','dodatni_troskovi']
    assert 'v2_finance_evaluated' in fx.client.get('/api/audit').text
    assert fx.client.get('/api/workspace').json()['workspace'] is None  # obračun ništa ne upisuje u radni prostor
    assert fx.client.post('/api/v2/finance',json=body,headers={'Origin':'https://evil.example'}).status_code==403
    assert fx.client.post('/api/v2/finance',json={'effects':'x'},headers=fx.headers).status_code==400
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','0')
    assert fx.client.post('/api/v2/finance',json=body,headers=fx.headers).status_code==404
    assert fx.client.get('/api/v2/finance/models').status_code==404
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.post('/api/v2/finance',json=body,headers=fx.headers).status_code==401
