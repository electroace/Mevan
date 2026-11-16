"""Faza 6a integracije 65/6: premium PDF (naslovnica, pregled, metodologija, radar, strane po modulima)."""
import subprocess
from pathlib import Path

import pytest

import mevan_premium_pdf as premium
import test_project_execution as project_fixture

# Ocjene simulacije DRVONOVA iz integracijskog paketa (MEVAN_TRI_KOMPANIJE_65_OCJENA.csv, kolona wood_score_v10).
WOOD='M08:2 S01:2 S02:1 S03:2 S04:2 S05:2 S06:1 S07:2 S08:2 F01:2 F02:1 F03:2 F04:2 F08:1 F09:2 F10:2 F13:2 O01:2 O02:2 O03:2 O05:1 O06:1 O07:2 O08:2 O09:1 O10:2 O11:2 O13:2 O14:2 O15:2 O16:1 P01:1 P02:0 P03:1 P04:1 P05:2 P06:1 P07:1 P08:2 P09:1 P10:1 P11:1 P12:1 P14:0 L01:3 L02:3 L03:3 L04:3 L05:3 L06:3 L07:3 L08:3 L10:3 L11:3 L12:3 M03:2 M04:2 M05:2 M06:1 M07:2 M09:2 M10:2 M11:2 M13:2 M14:2'


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def wood(simulated=True,**extra):
    assess={pair.split(':')[0]:{'score':int(pair.split(':')[1]),'proof':'confirmed','evidence':'Ogledni dokaz','finding':'Ogledni nalaz'} for pair in WOOD.split()}
    return {'company':'DRVONOVA','diagnostic':'Simulacija','generated':'16.11.2026.','assess':assess,'simulated':simulated,**extra}


def pages(data,tmp_path,layout=False):
    """Tekst po stranama. Bez rasporeda (zadano) tekst ide blok po blok, pa rečenice u kolonama ostaju cijele."""
    path=tmp_path/'premium.pdf';path.write_bytes(premium.render(data))
    text=subprocess.check_output(['pdftotext']+(['-layout'] if layout else [])+[str(path),'-']).decode()
    return [page for page in text.split('\f') if page.strip()],path


def flat(text):
    return ' '.join(text.split())


def test_engine_reproduces_the_reference_report_numbers_from_the_package_scores():
    report=premium.prepare(wood())
    # Uzor iz paketa navodi 36,6 ukupno i 35,6 / 35,0 / 34,3 / 20,0 / 60,0 / 38,0 po modulima.
    assert report['findings']['maturity']['index']==36.6
    assert {m['code']:m['index'] for m in report['modules']}=={'S':35.6,'F':35.0,'O':34.3,'P':20.0,'L':60.0,'M':38.0}
    assert {m['code']:m['criteria'] for m in report['modules']}=={'S':9,'F':8,'O':14,'P':13,'L':11,'M':10}


def test_every_page_carries_identity_status_and_page_number(tmp_path):
    result,_=pages(wood(),tmp_path,layout=True)
    assert len(result)>=10
    assert 'DRVONOVA' in result[0] and 'DIJAGNOSTIKA POSLOVNE ZRELOSTI' in result[0] and '36.6 / 100' in result[0] and '65 / 65' in result[0]
    for number,page in enumerate(result[1:],2):
        assert 'MEVAN / DIAGNOSTIC' in flat(page) and 'SIMULACIJA · NACRT METODOLOGIJE 65/6 · NEODOBRENO' in flat(page),number
        assert f'{number:02d}' in page.strip().splitlines()[-1],number


def test_report_sections_and_values_come_from_the_data(tmp_path):
    result,_=pages(wood(),tmp_path)
    text=flat(' '.join(result))
    for expected in ('Odluka na jednoj strani','Šta znači indeks zrelosti?','Mapa organizacijske zrelosti','ANALIZA MODULA 1/6','ANALIZA MODULA 6/6',
                     'Planiranje i Supply Chain ima najniži indeks: 20.0/100','Ljudi, organizacija i liderstvo 60.0/100 naspram Planiranje i Supply Chain 20.0/100',
                     '35.6/100','34.3/100','38.0/100','Nepoznato, neprocijenjeno i neprimjenjivo ne ulazi ni u zbir ni u nazivnik',
                     'Projektne opcije nisu unesene','M08 Upravljanje rizicima','Uzrok je HIPOTEZA','Prikazana su tri kandidata s najnižom ocjenom'):
        assert expected in text,expected
    assert 'POTVRĐEN_UZROK' not in text and 'Uzrok potvrđen dokazom' not in text  # simulacija ne može imati potvrđen uzrok


def test_real_data_is_not_labelled_simulation_but_stays_a_draft(tmp_path):
    result,_=pages(wood(simulated=False),tmp_path)
    text=flat(' '.join(result))
    assert 'SIMULACIJA' not in text and 'NACRT METODOLOGIJE 65/6 · NEODOBRENO' in text and 'potvrđeno' in text


def test_empty_diagnostic_renders_without_zero_indices(tmp_path):
    result,_=pages({'company':'Prazna d.o.o.','assess':{}},tmp_path)
    text=flat(' '.join(result))
    assert 'Neocjenjivo' in text and 'Nijedan modul još nema potvrđene ocjene' in text
    # Jedina nula je pokrivenost dokazima u pouzdanosti: to je poznata vrijednost (0 potvrđenih od 65), a ne nepoznato prikazano kao nula.
    assert text.count('0.0/100')==1 and '0.0/100 × 30 %' in text
    assert 'Radar nije zatvoren' in text and 'Za poređenje modula potrebne su potvrđene ocjene u najmanje dva modula.' in text


def test_ranked_options_and_financial_columns_appear_when_entered(tmp_path):
    src=lambda v:{'value':v,'source':'ERP','period':'2026'}
    effect={'id':'E1','criterion':'O03','model':'OEE','inputs':{'dodatne_prodane_jedinice_zbog_ogranicenja':src(2000),'kontribucija_po_jedinici':src(55),'dodatni_troskovi':src(10000)},
            'key':{'site':'Pogon','period':'2027','account':'6001','item':'Linija'},'status':'hypothesis'}
    option=lambda i,title,value:{'id':i,'title':title,'type':'project','criteria':['P02'],'ratings':{f:{'value':value,'rationale':'Procjena.'} for f in ('profit','liquidity','delivery','risk','feasibility')},
                               'business_case':'Slučaj','owner':'Direktor','budget_km':1000,'resources':'Tim','kpi':'KPI','steps_30':['Prvi korak '+i],'steps_90':['Kasniji korak']}
    result,_=pages(wood(effects=[effect],options=[option('P1','Pilot planiranja',5),option('P2','Zalihe',4),option('P3','Odgoda',3)]),tmp_path)
    text=flat(' '.join(result))
    assert '01 Pilot planiranja' in text and 'Prvi korak P1' in text and 'Konačan rang. Rang nije odobrenje ulaganja ni potvrda koristi.' in text
    # Tri kutije stoje jedna pored druge, pa se redovi teksta u izvodu prepliću; dijelovi rečenice se provjeravaju zasebno.
    assert 'Hipotetički potencijal: 100.000' in text and 'nije potvrđena korist' in text and 'POTVRĐENI GODIŠNJI EFEKAT' in text and '0 KM' in text


def test_longest_texts_and_long_names_flow_without_errors(tmp_path):
    data=wood()
    long=('Vrlo dug nalaz konsultanta koji mora preći preko više redova i strana. '*90)[:6000]
    for code in ('P02','P14','S02'):
        data['assess'][code]['finding']=long
    data['company']='Proizvodno preduzeće s veoma dugim nazivom d.o.o. Bosanska Krupa'
    result,_=pages(data,tmp_path)
    assert len(result)>=12 and 'Vrlo dug nalaz konsultanta' in flat(' '.join(result))


def test_bundled_fonts_are_embedded(tmp_path):
    _,path=pages(wood(),tmp_path)
    fonts=subprocess.check_output(['pdffonts',str(path)]).decode()
    for name in ('SourceSans3-Regular','SourceSans3-Semibold','SourceSerif4-Semibold'):
        line=next(l for l in fonts.splitlines() if name in l)
        assert ' yes ' in line,line  # ugrađen u dokument


def test_api_returns_pdf_only_for_logged_in_same_origin_requests(fx,monkeypatch):
    ok=fx.client.post('/api/v2/report/premium',json=wood(),headers=fx.headers)
    assert ok.status_code==200 and ok.content.startswith(b'%PDF') and ok.headers['content-type']=='application/pdf'
    assert 'v2_premium_pdf' in fx.client.get('/api/audit').text
    assert fx.client.post('/api/v2/report/premium',json={'assess':'x'},headers=fx.headers).status_code==400
    assert fx.client.post('/api/v2/report/premium',json=wood(),headers={'Origin':'https://evil.example'}).status_code==403
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','0')
    assert fx.client.post('/api/v2/report/premium',json=wood(),headers=fx.headers).status_code==404
    monkeypatch.setenv('MEVAN_METHODOLOGY_V2','1')
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.post('/api/v2/report/premium',json=wood(),headers=fx.headers).status_code==401


def test_page_offers_the_premium_pdf_only_through_the_server():
    html=(Path(premium.__file__).parent/'index.html').read_text(encoding='utf-8')
    assert 'onclick="downloadPremiumPdf()">Premium PDF (nacrt)</button>' in html
    assert "fetch('/api/v2/report/premium',{method:'POST'" in html and "if(METHOD.active!=='v2')return mvNotify('Premium PDF je dostupan za dijagnostike modela 65/6.',true);" in html


# ---- faza 6b: uzročni lanac, finansije, pouzdanost, rang, plan i dodatak

def full(**extra):
    src=lambda v:{'value':v,'source':'ERP','period':'2026'}
    effects=[{'id':'E1','criterion':'O03','model':'OEE','inputs':{'dodatne_prodane_jedinice_zbog_ogranicenja':src(2000),'kontribucija_po_jedinici':src(55),'dodatni_troskovi':src(10000)},
              'key':{'site':'Pogon','period':'2027','account':'6001','item':'Linija'},'status':'hypothesis'},
             {'id':'E2','criterion':'P10','model':'OTIF','inputs':{'izbjegnuti_penali':src(6000)},'key':{},'status':'hypothesis'},
             {'id':'E3','criterion':'S01','model':'OEE','inputs':{},'key':{},'status':'hypothesis'}]
    option=lambda i,title,value,**k:dict({'id':i,'title':title,'type':'project','criteria':['P02'],'ratings':{f:{'value':value,'rationale':'Procjena.'} for f in ('profit','liquidity','delivery','risk','feasibility')},
                                       'business_case':'Slučaj','owner':'Direktor','budget_km':1000,'resources':'Tim','kpi':'KPI','steps_30':['Prvi korak'],'steps_90':['Kasniji korak']},**k)
    plan=[{'task':'Pilot S&OP sastanak','owner':'Direktor','due':'','kpi':'Pridržavanje plana','status':'Nije počelo'},{'task':'Pregled rezultata','owner':'','due':'2027-02-15','kpi':'','status':'U toku'}]
    return wood(effects=effects,options=[option('P1','Pilot planiranja',5),option('P2','Zalihe',4),option('P3','Odgoda',3,type='defer',criteria=[])],plan=plan,**extra)


def test_full_report_has_every_required_section(tmp_path):
    result,_=pages(full(),tmp_path)
    text=flat(' '.join(result))
    for section in ('UZROČNA ANALIZA','Od nalaza do uzroka','FINANSIJSKI EFEKTI','Šta je potvrđeno, a šta hipoteza','POUZDANOST NALAZA','Zašto nalazu vjerujemo',
                    'PROJEKTNE OPCIJE','Koja opcija ima prioritet?','PLAN 90 DANA','Prvi koraci','DODATAK','Svih 65 kriterija'):
        assert section in text,section
    assert len(result)>=15


def test_causal_chain_shows_one_finding_and_never_claims_links_between_criteria(tmp_path):
    text=flat(' '.join(pages(full(),tmp_path)[0]))
    # Najniža ocjena u simulaciji je 0 (P02, zatim P14); lanac prikazuje prvi po šifri.
    assert 'P02 · S&OP / IBP · 0/5' in text and 'UZROK — HIPOTEZA' in text and 'POSLOVNA POSLJEDICA — HIPOTEZA' in text
    assert 'Veze između kriterija nisu modelirane' in text and 'Bez konkurentskog objašnjenja uzrok ostaje hipoteza.' in text
    assert 'OSTALI KANDIDATI ZA SLABOST' in text and 'UZROK — POTVRĐEN DOKAZOM' not in text


def test_finance_page_keeps_columns_apart_and_explains_blocked_effects_in_words(tmp_path):
    text=flat(' '.join(pages(full(),tmp_path)[0]))
    assert 'SIMULACIJA: NIŠTA NIJE POTVRĐENO' in text and 'HIPOTETIČKI POTENCIJAL' in text and 'GODIŠNJI P&L PO EFEKTIMA (JEDNA KOLONA)' in text
    assert 'Zbir uključuje hipoteze i zato nije potvrđena korist.' in text
    assert 'blokiran: nedostaju ulazi formule' in text and 'blokiran: kriterij nema finansijski model' in text and 'podaci su simulacija' in text
    for code in ('NEDOSTAJU_ULAZI','NEMA_AUTOMATSKE_MONETIZACIJE','PODACI_SU_SIMULACIJA','NEPOTPUN_KLJUC'):
        assert code not in text,code  # tehničke oznake se ne prikazuju čitaocu


def test_every_engine_reason_code_has_a_readable_text():
    for code in ('NEMA_AUTOMATSKE_MONETIZACIJE','MODEL_NIJE_DOZVOLJEN_ZA_KRITERIJ','NEPOZNAT_KRITERIJ','NEDOSTAJU_ULAZI: a, b','IZNOS_NIJE_POZITIVAN',
                 'ULAZI_BEZ_IZVORA_ILI_PERIODA: a','NIJE_OZNACEN_KAO_POTVRDJEN','NEDOSTAJE_DOKAZ','NEDOSTAJE_KONTRAFAKTUAL','NEDOSTAJE_ODOBRENJE_KONSULTANTA',
                 'NEPOTPUN_KLJUC','PODACI_SU_SIMULACIJA','ISTI_KLJUC_KAO_E1','MOGUCE_PREKLAPANJE_S_E2','USTUPLJENO_EFEKTU_E3'):
        readable=premium.reason_text(code)
        assert readable!=code and readable==readable.lower().replace('e1','E1').replace('e2','E2').replace('e3','E3') or 'E' in readable,code
    assert premium.reason_text('ISTI_KLJUC_KAO_E1')=='isti ključ kao efekat E1' and premium.reason_text('NEPOZNATA_OZNAKA')=='NEPOZNATA_OZNAKA'


def test_confidence_ranking_and_plan_pages_show_engine_values(tmp_path):
    text=flat(' '.join(pages(full(),tmp_path)[0]))
    assert 'Nepoznato: nema podataka za ovu komponentu. Nije nula.' in text and 'privremeni i nisu empirijski kalibrisani' in text
    assert '01 Pilot planiranja' in text and '100.0/100' in text and '03 Odgoda (odgoda / bez ulaganja)' in text and 'KONAČAN RANG' in text and 'v2-2026-11-11' in text
    assert 'Pilot S&OP sastanak' in text and 'nije određen' in text and '2027-02-15' in text and 'nije dodijeljen' in text and 'nije definisan' in text


def test_appendix_lists_all_65_criteria_once_with_score_and_evidence_status(tmp_path):
    result,_=pages(full(),tmp_path)
    start=next(i for i,page in enumerate(result) if 'Svih 65 kriterija' in page)
    appendix=flat(' '.join(result[start:]))
    import mevan_methodology
    for criterion in mevan_methodology.load('v2')['criteria']:
        assert appendix.count(criterion['code']+' '+criterion['name'])==1,criterion['code']
    assert 'potvrdio konsultant' in appendix and 'djelimično razvijeno' in appendix


def test_empty_sections_say_so_instead_of_inventing_content(tmp_path):
    text=flat(' '.join(pages({'company':'Prazna d.o.o.','assess':{}},tmp_path)[0]))
    for sentence in ('Nema kandidata za slabost s ocjenom i dokazom, pa se uzročni lanac ne može prikazati.','Finansijski efekti nisu uneseni.',
                     'Projektne opcije nisu unesene.','Plan 90 dana nije unesen.','Indeks je nepoznat jer nedostaju podaci'):
        assert sentence in text,sentence
    assert text.count('Nepoznato')>=65  # dodatak: nijedan kriterij nije prikazan kao 0/5
    assert ' 0/5' not in text
