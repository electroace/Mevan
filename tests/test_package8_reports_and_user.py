"""Osmi paket: isti izgled preostalih izvještaja i prijavljeni korisnik u zaglavlju."""
import io
import re
import subprocess
from pathlib import Path

import pytest
from docx import Document

import mevan_nav
import project_reports
import test_project_execution as project_fixture
from test_project_reports import sample

ROOT=Path(mevan_nav.__file__).parent


@pytest.fixture
def fx():
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def test_logged_in_user_is_shown_on_every_screen(fx):
    import server
    for path in ('/','/projects-ui','/dashboard-ui','/diagnostic-review'):
        html=fx.client.get(path).text
        header=html[html.index('<header class="mv-top">'):html.index('</header>')]
        assert header.count('class="mv-user"')==1 and '<b>'+server.EMAIL+'</b>' in header,path


def test_user_name_is_escaped_and_optional():
    page='<!--MEVAN_NAV_CSS--><!--MEVAN_SHELL_START--><!--MEVAN_SHELL_END-->'
    assert '<div class="mv-user"' not in mevan_nav.render_page(page,'projects')
    html=mevan_nav.render_page(page,'projects','a"<b>@x.test')
    assert 'a&quot;&lt;b&gt;@x.test' in html and 'a"<b>@x.test' not in html


def test_project_report_pdf_has_numbered_pages_and_sections(tmp_path):
    path=tmp_path/'project.pdf';path.write_bytes(project_reports.export_pdf(sample()))
    text=subprocess.check_output(['pdftotext','-layout',str(path),'-']).decode()
    pages=[page for page in text.split('\f') if page.strip()]
    for number,page in enumerate(pages,1):
        assert 'MEVAN' in page and f'Strana {number} / {len(pages)}' in page
    for expected in ('IZVJEŠTAJ O OPERATIVNOM PROJEKTU','RADNI IZVJEŠTAJ — procjene nisu potvrđeni rezultati.','01','Identifikacija projekta','Projektni Charter','Status potvrde efekata'):
        assert expected in text,expected


def test_project_report_word_keeps_paragraph_text():
    document=Document(io.BytesIO(project_reports.export_docx(sample())))
    text='\n'.join(p.text for p in document.paragraphs)
    for expected in ('Izvještaj o operativnom projektu',project_reports.WORKING_NOTE,'01   Identifikacija projekta','Status: draft'):
        assert expected in text,expected
    assert document.sections[0].header.paragraphs[0].text=='MEVAN 4.0 | Konsultantski izvještaj'
    assert document.sections[0].footer.paragraphs[0].text.endswith('\tStrana ')
    demo=sample();demo['charter']['report_mode']='demo'
    section=Document(io.BytesIO(project_reports.export_docx(demo))).sections[0]
    assert section.header.paragraphs[0].text==project_reports.DEMO_LABEL
    assert section.footer.paragraphs[0].text.startswith(project_reports.DEMO_FOOTER)


def test_browser_word_exports_share_one_package_builder():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert html.count('function docxEntries(paras,footerText){')==1 and html.count('function docxTable(rows){')==1
    assert html.count('const entries=docxEntries(paras,')==2 and html.count('paras.push(docxTable(rows))')==2
    builder=html[html.index('function docxEntries('):html.index('function exportDOCX(')]
    for part in ("'word/header1.xml'","'word/footer1.xml'","'word/_rels/document.xml.rels'",'PAGE</w:instrText>','w:headerReference','w:footerReference'):
        assert part in builder,part
    # Redoslijed svojstava teksta prati Word shemu: pismo, podebljano, boja, veličina.
    assert re.search(r'<w:rFonts [^>]*/>\$\{bold\?\'<w:b/>\':\'\'\}<w:color [^>]*/><w:sz ',builder)
