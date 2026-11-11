"""Deseti paket, korak 1: izbor jezika, engleski meni, prijava i fiksni natpisi."""
import re
from pathlib import Path

import pytest

import mevan_i18n
import mevan_nav
import test_project_execution as project_fixture

ROOT=Path(mevan_nav.__file__).parent
SCREENS=('/','/projects-ui','/dashboard-ui','/diagnostic-review')


@pytest.fixture
def fx():
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def test_default_language_is_bosnian_and_sends_no_dictionary(fx):
    html=fx.client.get('/').text
    assert html.startswith('<!doctype html><html lang="bs">')
    assert 'window.MV_LANG="bs";window.MV_I18N={};' in html
    assert '<p class="mv-label">Kompanija</p>' in html and '>Odjava</button>' in html


def test_language_choice_is_remembered_and_applies_to_every_screen(fx):
    r=fx.client.get('/lang/en?next=/projects-ui',follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/projects-ui' and 'mevan_lang=en' in r.headers['set-cookie']
    for path in SCREENS:
        html=fx.client.get(path).text
        assert '<html lang="en">' in html[:60],path
        nav=html[html.index('<nav class="mv-nav"'):html.index('</nav>')]
        for label in ('Company','Assessment','Analysis &amp; reports','Projects','Data &amp; security','Sign out','Guided collection'):
            assert '>'+label+'<' in nav,(path,label)
        header=html[html.index('<header class="mv-top">'):html.index('</header>')]
        assert '<small>Signed in as</small>' in header and 'data-lang="en" lang="en" title="English" aria-current="true"' in header
        assert 'window.MV_LANG="en"' in html and '"Sačuvaj": "Save"' in html
        assert '<button value="ok">Confirm</button><button value="cancel" formnovalidate>Cancel</button>' in html
    fx.client.get('/lang/bs',follow_redirects=False)
    assert '<p class="mv-label">Kompanija</p>' in fx.client.get('/').text


def test_unknown_language_and_foreign_return_address_are_refused(fx):
    assert fx.client.get('/lang/de',follow_redirects=False).status_code==404
    assert fx.client.get('/lang/en?next=https://evil.example/',follow_redirects=False).headers['location']=='/'
    assert fx.client.get('/lang/en?next=//evil.example',follow_redirects=False).headers['location']=='/'
    fx.client.cookies.set(mevan_i18n.COOKIE,'<script>')
    assert '<html lang="bs">' in fx.client.get('/').text[:60]


def test_login_page_follows_the_language(fx):
    import server
    english=server.login_html('Pogrešna prijava. Provjerite e-mail i lozinku pa pokušajte ponovo.','en')
    for text in ('<html lang="en">','<title>MEVAN – sign in</title>','<h1>Sign in</h1>','>Email</label>','>Password</label>','<button>Sign in</button>','Sign-in failed.'):
        assert text in english,text
    bosnian=server.login_html()
    assert '<h1>Prijava</h1>' in bosnian and 'href="/lang/en?next=/login"' in bosnian


def test_dictionary_keys_exist_in_the_interface_and_have_translations():
    sources=''.join((ROOT/name).read_text(encoding='utf-8') for name in ('index.html','projects_ui.html','dashboard_ui.html','diagnostic_review.html','mevan_nav.py','server.py','approved_reports.py','mevan_report_model.py'))
    import approved_reports
    sources+=approved_reports.DEMO_NOTICE+approved_reports.DEMO_FOOTER  # sastavljeni iz DEMO oznake
    missing=[key for key in mevan_i18n.EN if key not in sources]
    assert not missing,missing
    assert all(isinstance(value,str) and value.strip() for value in mevan_i18n.EN.values())


def test_script_data_cannot_break_out_of_the_page():
    script=mevan_i18n.client_script('en')
    assert script.count('</script>')==1 and script.endswith('</script>')


def test_translator_leaves_user_content_alone():
    js=mevan_nav.JS
    assert "SKIP={SCRIPT:1,STYLE:1,TEXTAREA:1}" in js and "parent.closest('[translate=no],.mv-user')" in js
    assert "parent.nodeName==='OPTION'&&!parent.hasAttribute('value')" in js
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    for marked in ('<h1 translate="no">${esc(state.company.name','<select id="companySelect" translate="no">','<strong translate="no">${esc(x.name)}','<span class="fx-name" translate="no">'):
        assert marked in index,marked


# ---- korak 2: tekstovi s brojevima i zaključani izvještaji

def test_number_patterns_compile_and_keep_their_groups():
    for source,target in mevan_i18n.PATTERNS:
        groups=re.compile(source).groups
        used={int(n) for n in re.findall(r'\$(\d)',target)}
        assert used and max(used)<=groups,(source,target)
    script=mevan_i18n.client_script('en')
    assert 'window.MV_I18N_PATTERNS=[[' in script and mevan_i18n.client_script('bs').endswith('window.MV_I18N_PATTERNS=[];</script>')


def test_format_templates_keep_the_same_placeholders():
    for source,target in mevan_i18n.EN.items():
        if re.search(r'\{[a-z]\}',source):
            assert sorted(re.findall(r'\{[a-z]\}',source))==sorted(re.findall(r'\{[a-z]\}',target)),source


from test_package2 import api, approve, doc_text, save  # noqa: E402,F401  (postojeći pomoćnici za zaključani izvještaj)
from test_approved_delivery import diagnostic  # noqa: E402


@pytest.mark.parametrize('fmt',['pdf','docx'])
def test_locked_report_labels_follow_the_language_but_content_does_not(api,fmt):
    client,_,tmp_path=api
    d=diagnostic('QA-jezik')
    assert save(client,d).status_code==200
    aid=approve(client).json()['approval_id']
    bosnian,_,_=doc_text(client,aid,'detailed',fmt,tmp_path)
    english,_,_=doc_text(client,aid,'detailed',fmt,tmp_path,'?lang=en')
    flat=lambda text:' '.join(text.split())
    for label in ('Sažetak konsultanta','Tri prioriteta','Zrelost po oblastima','Plan za 90 dana','Ocjene i trag provjere dokaza','SHA-256 zaključanog snimka:'):
        assert label in flat(bosnian) and label not in flat(english),label
    for label in ('Consultant summary','Three priorities','Maturity by area','90-day plan','Scores and evidence audit trail','SHA-256 of the locked snapshot:','Overall index','Days 1–30','Finance'):
        assert label in flat(english),label
    # Tekst konsultanta i podaci snimka su isti na oba jezika.
    review=d['consultant_review']
    for own in (review['summary'],review['priority1'],review['month3']):
        assert flat(own) in flat(bosnian) and flat(own) in flat(english)
    client.cookies.set(mevan_i18n.COOKIE,'en')
    by_cookie,_,_=doc_text(client,aid,'detailed',fmt,tmp_path)
    assert 'Consultant summary' in flat(by_cookie)
    assert 'Sažetak konsultanta' in flat(doc_text(client,aid,'detailed',fmt,tmp_path,'?lang=bs')[0])


# ---- korak 3: katalog kriterija i Word izvozi iz preglednika

def test_english_catalogue_covers_all_61_criteria_with_the_same_structure():
    import json
    from mevan_criteria_en import CRITERIA_EN, FIELDS
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    source=json.loads(re.search(r'const CRITERIA=(\[.*?\]);\n',html,re.S).group(1))
    assert len(source)==61 and {c['code'] for c in source}==set(CRITERIA_EN)
    for criterion in source:
        english=CRITERIA_EN[criterion['code']]
        assert set(english)==set(FIELDS) and all(isinstance(v,str) and v.strip() for v in english.values()),criterion['code']
        assert 'dim' not in english and 'code' not in english  # šifra i dimenzija se nikad ne zamjenjuju
        assert english['question'].endswith('?')==criterion['question'].endswith('?'),criterion['code']
        assert (english['financial']==english['recommendation'])==(criterion['financial']==criterion['recommendation']),criterion['code']


def test_catalogue_is_sent_only_in_english_and_applied_before_use():
    assert 'window.MV_CRITERIA_EN={"F01"' in mevan_i18n.client_script('en') and 'MV_CRITERIA_EN' not in mevan_i18n.client_script('bs')
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    apply="if(typeof window!=='undefined'&&window.MV_LANG==='en'&&window.MV_CRITERIA_EN)for(const c of CRITERIA)Object.assign(c,window.MV_CRITERIA_EN[c.code]||{});"
    assert html.count(apply)==1 and html.index(apply)<html.index('const DIMS=[...new Set(CRITERIA.map(c=>c.dim))];')


def test_browser_word_exports_use_the_dictionary():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert html.count("if(typeof mvT==='function'&&typeof value==='string')value=mvT(value);")==1
    assert html.count("if(typeof mvT==='function'&&typeof v==='string')v=mvT(v);")==1
    assert "${typeof mvT==='function'?mvT('Strana'):'Strana'} " in html
