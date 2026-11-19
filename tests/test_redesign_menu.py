"""Redizajn 1 (19.11.2026.): meni po koracima rada i kontekst rada u zaglavlju."""
import re
from pathlib import Path

import pytest

import mevan_nav
import test_project_execution as project_fixture

ROOT=Path(mevan_nav.__file__).parent
PAGE='<html lang="bs"><!--MEVAN_NAV_CSS--><!--MEVAN_SHELL_START--><!--MEVAN_SHELL_END-->'


@pytest.fixture
def fx():
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def nav(active='diagnostic',lang='bs'):
    html=mevan_nav.render_page(PAGE,active,'a@b.test',lang)
    return html[html.index('<nav class="mv-nav"'):html.index('</nav>')]


def test_menu_follows_the_six_work_steps_in_order():
    groups=re.findall(r'<div class="mv-group"><p class="mv-label"><span class="mv-step">(\d)</span>([^<]+)</p>(.*?)</div>(?=<div class="mv-group">|<div class="mv-foot">)',nav(),re.S)
    assert [(number,title) for number,title,_ in groups]==[('1','Kompanija'),('2','Procjena'),('3','Nalazi'),('4','Finansije'),('5','Opcije i plan'),('6','Izvještaji')]
    items={title:re.findall(r'>([^<>]+)</(?:a|button)>',body) for _,title,body in groups}
    assert items['Kompanija']==['Kompanije i dijagnostike','Profil kompanije']
    assert items['Procjena'][0]=='Pregled' and len(items['Procjena'])==6  # pregled i pet modula modela 61/5 (65/6 ih zamijeni u pregledniku)
    assert items['Nalazi']==['Lanac nalaza','Integrisana analiza (AI)','Analiza i odobravanje']
    assert items['Finansije']==['Finansijski efekti']
    assert items['Opcije i plan']==['Projektne opcije','Plan 90 dana','Projekti','Pregled portfolija']
    assert items['Izvještaji']==['Izvještaji','Vođeno prikupljanje']


def test_every_page_of_the_app_is_reachable_from_the_menu_exactly_once():
    html=nav()
    assert mevan_nav.PAGES==('workspace','company','overview','findings','v2','review','finance','options','plan','report','data')
    for key in mevan_nav.PAGES:
        assert html.count(f'data-page="{key}"')==1,key
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    listed=re.search(r"const NAV_PAGES=\[([^\]]+)\]",index).group(1)
    for key in mevan_nav.PAGES:
        assert f"'{key}'" in listed,key


def test_items_that_exist_for_one_model_only_are_marked_and_hidden_for_the_other():
    html=nav()
    model=lambda label:re.search(r'<(?:a|button)[^>]*?(?: data-model="(v\d)")?[^>]*>'+re.escape(label)+'<',html).group(1)
    marks={label:(re.search(r'data-model="(v\d)"[^>]*>'+re.escape(label)+'<',html) or [None,None])[1] for label in
           ('Lanac nalaza','Projektne opcije','Integrisana analiza (AI)','Vođeno prikupljanje','Projekti','Pregled portfolija','Analiza i odobravanje','Plan 90 dana','Izvještaji','Finansijski efekti')}
    assert marks=={'Lanac nalaza':'v2','Projektne opcije':'v2','Integrisana analiza (AI)':'v1','Vođeno prikupljanje':'v1','Projekti':'v1','Pregled portfolija':'v1',
                   'Analiza i odobravanje':None,'Plan 90 dana':None,'Izvještaji':None,'Finansijski efekti':None}
    assert 'html[data-model="v2"] .mv-nav [data-model="v1"],html:not([data-model="v2"]) .mv-nav [data-model="v2"]{display:none}' in mevan_nav.CSS
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    assert "document.documentElement.dataset.model=wanted;" in index


def test_header_shows_work_context_instead_of_slogan_and_fixed_counts(fx):
    for path in ('/','/projects-ui','/dashboard-ui','/diagnostic-review'):
        html=fx.client.get(path).text
        header=html[html.index('<header class="mv-top">'):html.index('</header>')]
        assert header.count('<div class="mv-context" id="mvContext"></div>')==1,path
        assert '61 kriterij' not in header and 'PRIVATE DEMO' not in header and 'mv-sub' not in header
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    context=index[index.index('function renderContext(){'):index.index('async function addCompany(){')]
    for part in ("select('ctxCompany','Aktivna kompanija'","select('ctxDiagnostic','Aktivna dijagnostika'","'model 65/6 (nacrt)':'model 61/5'","badge('DEMO',true)","chooseCompany","chooseDiagnostic"):
        assert part in context,part
    assert "el.setAttribute('translate','no')" in context  # nazivi kompanija i dijagnostika se ne prevode
    assert '});renderContext();let html' in index


def test_findings_menu_item_always_recalculates_and_reports_page_offers_the_premium_pdf():
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    assert "if(b.dataset.page==='findings'&&METHOD.active==='v2')return openFindings();" in index
    report=index[index.index("else if(page==='report'){"):index.index("else if(page==='report'){")+2600]
    assert "(METHOD.active==='v2'?" in report and '<h2>Premium PDF</h2>' in report and 'downloadPremiumPdf()' in report


def test_menu_steps_are_translated():
    english=nav(lang='en')
    for label in ('>Company<','>Assessment<','>Findings<','>Finance<','>Options &amp; plan<','>Reports<','>Finding chain<','>Project options<'):
        assert label in english,label
