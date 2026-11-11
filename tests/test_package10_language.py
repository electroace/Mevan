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
    sources=''.join((ROOT/name).read_text(encoding='utf-8') for name in ('index.html','projects_ui.html','dashboard_ui.html','diagnostic_review.html','mevan_nav.py','server.py'))
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
