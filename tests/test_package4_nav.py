"""Paket 4: isti glavni meni i zaglavlje na sva četiri ekrana."""
import re
import pytest
import test_project_execution as project_fixture
import mevan_nav

SCREENS={'/':'diagnostic','/diagnostic-review':'guided','/projects-ui':'projects','/dashboard-ui':'portfolio'}


@pytest.fixture
def fx():
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


@pytest.mark.parametrize('path',sorted(SCREENS))
def test_every_screen_has_one_shared_menu(fx,path):
    r=fx.client.get(path)
    assert r.status_code==200
    html=r.text
    assert '<!--MEVAN_' not in html
    assert html.count('id="mvNav"')==1 and html.count('id="mvToggle"')==1
    assert html.count('action="/logout"')==1
    nav=html[html.index('<nav class="mv-nav"'):html.index('</nav>')]
    for group in ('Kompanija','Procjena','Analiza i izvještaji','Projekti'):
        assert f'<p class="mv-label">{group}</p>' in nav
    for key in mevan_nav.PAGES:
        assert html.count(f'data-page="{key}"')==1,key
    for key,_ in mevan_nav.MODULES:
        assert f'href="/#m:{key}"' in nav
    assert 'href="/projects-ui"' in nav and 'href="/dashboard-ui"' in nav
    assert 'aria-label="Vođeno prikupljanje i završni izvještaji"' in nav
    assert nav.index('Podaci i sigurnost')<nav.index('Odjava')
    for old in ('Project Execution TEST','Portfolio dashboard','← Dijagnostika','Projekti TEST'):
        assert old not in html,old


def test_current_screen_is_marked(fx):
    marks={path:re.findall(r'<(?:a|button)[^>]*aria-current="page"[^>]*>([^<]+)<',fx.client.get(path).text) for path in SCREENS}
    assert marks=={'/':[],'/diagnostic-review':['Vođeno prikupljanje'],'/projects-ui':['Projekti'],'/dashboard-ui':['Pregled portfolija']}


def test_screens_still_require_login(fx):
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    for path in SCREENS:
        r=fx.client.get(path,follow_redirects=False)
        assert r.status_code in (303,307) and r.headers['location']=='/login'


def test_server_backup_lives_on_data_page_not_in_a_floating_box():
    from pathlib import Path
    html=Path(mevan_nav.__file__).with_name('index.html').read_text(encoding='utf-8')
    assert html.count('id="mevan-backup-tools"')==1 and 'position:fixed;bottom:12px' not in html
    data_page=html[html.index("else if(page==='data')"):]
    assert 'id="mevan-restore-file"' in data_page[:3000] and 'href="/api/backup"' in data_page[:3000]
    assert 'async function mevanRestoreBackup()' in html


def test_unknown_screen_or_broken_page_is_rejected():
    with pytest.raises(ValueError):
        mevan_nav.nav_html('nepoznato')
    with pytest.raises(ValueError):
        mevan_nav.render_page('<html></html>','projects')
