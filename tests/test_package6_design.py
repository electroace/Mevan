"""Šesti paket: pristupačnost i ujednačen izgled. Poslovna logika nije mijenjana."""
import re
from pathlib import Path

import mevan_nav

ROOT=Path(mevan_nav.__file__).parent
PAGES=('index.html','projects_ui.html','dashboard_ui.html','diagnostic_review.html')


def _read(name):
    return (ROOT/name).read_text(encoding='utf-8')


def test_no_browser_dialogs_remain_on_any_screen():
    for name in PAGES:
        found=re.findall(r'(?<![A-Za-z.])(?:alert|confirm|prompt)\(',_read(name))
        assert not found,(name,found)


def test_shared_shell_provides_messages_dialog_and_label_linking():
    html=mevan_nav.render_page('<!--MEVAN_NAV_CSS--><!--MEVAN_SHELL_START--><!--MEVAN_SHELL_END-->','projects')
    assert html.count('id="mvToasts"')==1 and html.count('<dialog class="mv-dialog" id="mvDialog"')==1
    for name in ('window.mvNotify=','window.mvConfirm=','window.mvAsk=','window.mvLinkLabels='):
        assert name in mevan_nav.JS,name
    # Zadano dugme prozora je „Potvrdi” (Enter u polju), a fokus potvrde ide na „Odustani”.
    dialog=html[html.index('<dialog'):html.index('</dialog>')]
    assert dialog.index('value="ok"')<dialog.index('value="cancel"')


def test_secondary_text_colour_meets_contrast_everywhere():
    def luminance(colour):
        parts=[int(colour[i:i+2],16)/255 for i in (1,3,5)]
        parts=[c/12.92 if c<=.03928 else ((c+.055)/1.055)**2.4 for c in parts]
        return .2126*parts[0]+.7152*parts[1]+.0722*parts[2]
    def contrast(a,b):
        hi,lo=sorted((luminance(a),luminance(b)),reverse=True)
        return (hi+.05)/(lo+.05)
    muted=re.search(r'--mv-muted:(#[0-9a-f]{6})',mevan_nav.CSS).group(1)
    for background in ('#ffffff','#f3f7fa','#f2f5f8','#f3f6fa'):
        assert contrast(muted,background)>=4.5,background
    for name in PAGES+('mevan_nav.py',):
        text=_read(name)
        assert '#697d8e' not in text and '#637789' not in text,name


def test_overview_bar_shows_maturity_index_not_completion():
    html=_read('index.html')
    overview=html[html.index("else if(page==='overview')"):html.index("else if(page.startsWith('m:'))")]
    assert 'aria-label="Indeks zrelosti' in overview
    assert 'a.valid/a.app*100' not in overview


def test_financial_register_rows_are_collapsed_and_removal_is_confirmed():
    html=_read('index.html')
    assert '<details class="panel fx" data-fx="${esc(x.id)}"' in html
    assert 'onclick="removeEffect(${i})"' in html and 'onclick="removePlanItem(${i})"' in html
    assert "async function removePlanItem(i){if(!await mvConfirm(" in html


def test_reset_demo_is_separated_from_primary_actions():
    html=_read('index.html')
    workspace=html[html.index("if(page==='workspace')"):html.index("else if(page==='company')")]
    first_row=workspace[:workspace.index('</div>',workspace.index('addCompany()'))]
    assert 'resetDemo()' not in first_row and workspace.count('onclick="resetDemo()"')==1


def test_sync_status_is_visible_and_announced():
    html=_read('index.html')
    assert html.count('id="syncStatus" role="status"')==1
    assert "Object.defineProperty(globalThis,'cloudStatus'" in html


def test_login_page_is_labelled_and_shows_error_inline(monkeypatch):
    import server
    page=server.login_html()
    assert '<label for="email">' in page and '<label for="password">' in page and '<main>' in page
    assert 'role="alert"' not in page
    assert 'role="alert"' in server.login_html('Pogrešna prijava.')


# ---- 6.1: dugme „Odjava” u meniju

import pytest
import test_project_execution as project_fixture


@pytest.fixture
def fx():
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def _logout_token(html):
    form=html[html.index('action="/logout"'):]
    return re.search(r'name="csrf_token" value="([0-9a-f]{64})"',form[:300]).group(1)


def test_menu_logout_works_when_browser_sends_null_origin(fx):
    # Preglednik uz Referrer-Policy: no-referrer šalje obrazac s `Origin: null`.
    for path in ('/','/projects-ui','/dashboard-ui','/diagnostic-review'):
        assert '__MEVAN_LOGOUT_TOKEN__' not in fx.client.get(path).text
    token=_logout_token(fx.client.get('/').text)
    form={'Origin':'null','Content-Type':'application/x-www-form-urlencoded'}
    r=fx.client.post('/logout',content='csrf_token='+token,headers=form,follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/login'
    assert fx.client.get('/',follow_redirects=False).status_code in (303,307)


def test_logout_without_valid_token_or_origin_is_still_rejected(fx):
    form={'Origin':'null','Content-Type':'application/x-www-form-urlencoded'}
    assert fx.client.post('/logout',content='',headers=form,follow_redirects=False).status_code==403
    assert fx.client.post('/logout',content='csrf_token='+'0'*64,headers=form,follow_redirects=False).status_code==403
    other={'Origin':'https://evil.example','Content-Type':'application/x-www-form-urlencoded'}
    assert fx.client.post('/logout',content='csrf_token='+'0'*64,headers=other,follow_redirects=False).status_code==403
    assert fx.client.get('/',follow_redirects=False).status_code==200
