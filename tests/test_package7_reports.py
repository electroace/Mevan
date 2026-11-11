"""Sedmi paket: izgled zaključanih izvještaja (PDF i Word) i meni koji staje na ekran.

Sadržaj izvještaja i obračuni nisu mijenjani; ovdje se provjerava samo prikaz.
"""
import io
import subprocess
from pathlib import Path

import pytest
from docx import Document

import approved_reports
import mevan_nav
import mevan_report_fonts
from mevan_report_model import DEMO_LABEL


def content(**changes):
    base={
        'demo':True,'modern':True,'view':'detailed','kind':'Detaljni stručni izvještaj','company':'Čelik d.o.o. Žepče',
        'diagnostic':'Početna dijagnostika · ID d-1',
        'meta':[('DEMO snimak','7'),('Revizija','3'),('Pripremio','qa@example.test'),('Zaključano (UTC)','11.11.2026. 09:48')],
        'summary':'Sažetak s našim slovima: č, ć, ž, š, đ.','priorities':['Prvi prioritet','Drugi prioritet','Treći prioritet'],
        'selection':'Odabrani prioritet: C2 · Projektni nacrt: p-1','selected':1,'index':36.0,'criteria_count':61,
        'scope':'Primjenjivo 60/61 · N/P 1. N/P je isključen iz nazivnika; nepoznato nije ocjena nula.',
        'dimensions':[{'name':name,'index':value,'scope':'primjenjivo 12, N/P 0'} for name,value in
                      (('Finansije',36.4),('Operacije',34.7),('Planiranje',35.0),('Ljudi',42.0),('Upravljanje',33.3))],
        'not_applicable':['F01 · N/P · Proces nije primjenjiv u ovom obuhvatu. · Potvrdio konsultant: qa@example.test'],
        'scenarios':[{'name':'Smanjenje škarta','amount':'9450 KM godišnje','reason':'Nije potvrđena osnovica'}],
        'plan':[('1–30 dana','Prvi period'),('31–60 dana','Drugi period'),('61–90 dana','Treći period')],
        'criteria':[{'code':'F01','name':'Profitabilnost','score':None,'collection':[('Intervju','Bilješka s intervjua')]},
                    {'code':'F02','name':'Kontribucijska marža','score':1,'evidence':'Dokaz F02','source':'Izvor ERP · Period 2026-01 – 2026-10',
                     'trace':'Procijenio qa · Trag A-1','collection':[('Intervju','Nije prikupljeno')],'finding':'Nalaz za F02'},
                    {'code':'O01','name':'OEE','score':4,'evidence':'Dokaz O01','source':'Izvor MES · Period — – —','trace':'Procijenio qa · Trag A-2','collection':[],'finding':''}],
        'sha256':'ab'*32,
    }
    base.update(changes)
    return base


def pdf_text(data,tmp_path):
    path=tmp_path/'report.pdf';path.write_bytes(data)
    return subprocess.check_output(['pdftotext','-layout',str(path),'-']).decode()


def test_bundled_fonts_exist_and_are_used():
    paths=mevan_report_fonts.font_paths()
    assert set(paths)=={'body','bold','display'}
    assert all(Path(path).parent.name=='fonts' and Path(path).is_file() for path in paths.values())
    assert (mevan_report_fonts.DIR/'OFL-LICENSE.md').is_file()


def test_reports_still_render_without_the_fonts_directory(monkeypatch,tmp_path):
    monkeypatch.setattr(mevan_report_fonts,'DIR',tmp_path/'nema')
    assert set(mevan_report_fonts.font_paths().values())=={mevan_report_fonts.FALLBACK}
    assert approved_reports.render_pdf(content()).startswith(b'%PDF')
    assert approved_reports.render_docx(content())[:2]==b'PK'


def test_pdf_has_page_furniture_and_all_content(tmp_path):
    text=pdf_text(approved_reports.render_pdf(content()),tmp_path)
    pages=[page for page in text.split('\f') if page.strip()]
    for number,page in enumerate(pages,1):
        assert 'MEVAN' in page and DEMO_LABEL+' — nije stvarni provjereni nalaz' in page
        assert f'Strana {number} / {len(pages)}' in page
    for expected in ('Čelik d.o.o. Žepče','č, ć, ž, š, đ','ODABRAN ZA PROJEKAT','Ukupni indeks 36.0/100 · 61 kriterija','Primjenjivo 60/61',
                     'Finansije','36.4','Smanjenje škarta','procjena 9450 KM godišnje','61–90 dana','FINANSIJE','OPERACIJE',
                     'F01 · Profitabilnost · N/P (isključeno iz obračuna)','F02 · Kontribucijska marža','1/5','4/5','Nalaz za F02','SHA-256 zaključanog snimka: '+'ab'*32):
        assert expected in text,expected


def test_unscored_area_is_never_drawn_or_printed_as_zero(tmp_path):
    empty=content(index=None,dimensions=[{'name':'Finansije','index':None,'scope':''}])
    path=tmp_path/'empty.pdf';path.write_bytes(approved_reports.render_pdf(empty))
    text=' '.join(subprocess.check_output(['pdftotext',str(path),'-']).decode().split())
    assert 'Neocjenjivo — nema ocijenjenih primjenjivih kriterija' in text and '0/100' not in text
    word='\n'.join(p.text for p in Document(io.BytesIO(approved_reports.render_docx(empty))).paragraphs)
    assert 'Finansije · Neocjenjivo' in word and '0/100' not in word


def test_longest_allowed_texts_flow_across_pages(tmp_path):
    long=('Rečenica koja popunjava dozvoljenu dužinu polja. '*130)[:6000]
    data=approved_reports.render_pdf(content(summary=long,priorities=[long]*3,plan=[(p,long) for p in approved_reports.PERIODS]))
    assert len([page for page in pdf_text(data,tmp_path).split('\f') if page.strip()])>=5


def test_word_report_keeps_text_in_paragraphs_with_one_chart():
    document=Document(io.BytesIO(approved_reports.render_docx(content())))
    text='\n'.join(p.text for p in document.paragraphs)
    for expected in ('Čelik d.o.o. Žepče','01   Sažetak konsultanta','2.\tDrugi prioritet  — odabran za projekat','Ukupni indeks 36.0/100 · 61 kriterija',
                     'Finansije · 36.4/100 · primjenjivo 12, N/P 0','Smanjenje škarta · procjena 9450 KM godišnje · Nije potvrđena osnovica',
                     'F02 · Kontribucijska marža · 1/5','Intervju: Nije prikupljeno','SHA-256 zaključanog snimka: '+'ab'*32):
        assert expected in text,expected
    section=document.sections[0]
    assert section.header.paragraphs[0].text==DEMO_LABEL
    assert section.footer.paragraphs[0].text.startswith(DEMO_LABEL+' — nije stvarni provjereni nalaz')
    assert len(document.inline_shapes)==1
    real=Document(io.BytesIO(approved_reports.render_docx(content(demo=False))))
    assert real.sections[0].header.paragraphs[0].text=='MEVAN  /  Dijagnostika'
    assert DEMO_LABEL not in '\n'.join(p.text for p in real.paragraphs)


def test_menu_fits_the_screen_and_logout_stays_visible():
    assert 'max-height:calc(100vh - var(--mv-head,76px) - 32px)' in mevan_nav.CSS
    foot=mevan_nav.CSS[mevan_nav.CSS.index('.mv-nav .mv-foot{'):]
    assert 'position:sticky;bottom:0' in foot[:foot.index('}')]
    assert "root.style.setProperty('--mv-head'" in mevan_nav.JS
