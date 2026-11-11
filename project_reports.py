"""On-demand project reporting. No new verification or annualisation claims."""
from io import BytesIO
from pathlib import Path
import reportlab
from xml.sax.saxutils import escape
from datetime import datetime, timezone
from docx import Document
from docx.shared import Pt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from project_actuals import summarize
from project_finance import FinancialModel, calculate
from mevan_report_model import DEMO_LABEL

FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
if not FONT.is_file():
    FONT = Path(reportlab.__file__).parent / 'fonts' / 'Vera.ttf'
FONT = str(FONT)

def clean(v):
    if v is None or v == '': return 'Nije uneseno'
    if isinstance(v,bool):return 'Da' if v else 'Ne'
    return str(v)

def build_sections(data):
    ch=data['charter']; sections=[]
    def add(title,items):sections.append((title,[(clean(k),clean(v)) for k,v in items]))
    if ch.get('report_mode')=='demo':add(DEMO_LABEL,[('Ograničenje','Nije stvarni odobreni projekat; nema provjerenih rezultata.')])
    add('Identifikacija projekta', [('Kompanija',data['company_id']),('Dijagnostika',data['diagnostic_id']),('Status',data['status']),('Datum odobrenja',datetime.fromtimestamp(data['approved_at'],timezone.utc).strftime('%d.%m.%Y') if data.get('approved_at') else 'Nije odobreno')])
    add('Projektni Charter',[('Problem',ch.get('problem')),('Cilj',ch.get('objective')),('Obim',ch.get('scope')),('Metodologija',ch.get('methodology'))])
    add('Pretpostavke i validacija',[(f'Pretpostavka {i}',v) for i,v in enumerate(ch.get('assumptions',[]),1)]+[(f'Provjera {i}',v) for i,v in enumerate(ch.get('required_checks',[]),1)]+[('Početno stanje provjereno',ch.get('baseline_verified',False)),('Ciljevi odobreni',ch.get('targets_approved',False)),('Provjere završene',ch.get('checks_completed',False))])
    add('Aktivnosti',[(f'Aktivnost {i}', ' | '.join(f'{k}: {clean(v)}' for k,v in a.items() if v is not None)) for i,a in enumerate(ch.get('activities',[]),1)] or [('Stanje','Nisu definisane')])
    add('KPI registar',[(f'KPI {i}', ' | '.join(f'{k}: {clean(v)}' for k,v in a.items() if v is not None)) for i,a in enumerate(ch.get('kpis',[]),1)] or [('Stanje','Nisu definisani')])
    finance=data.get('finance')
    if finance:
        calc=calculate(FinancialModel.model_validate(finance))
        add('Finansijski scenariji — isključivo procjene',[(s['name'],f"Godišnji neto efekat: {s['annual_net_benefit_km']} KM; jednokratni obrtni kapital: {s['one_time_working_capital_release_km']} KM; implementacija: {s['implementation_cost_km']} KM; ROI: {clean(s['simple_annual_roi_percent'])}%; povrat: {clean(s['simple_payback_months'])} mjeseci") for s in calc['scenarios']]+[('Upozorenje',calc['warning']),('Metodologija',calc['methodology'])])
    else:add('Finansijski scenariji',[('Stanje','Finansijski model nije unesen')])
    reviews=data.get('reviews',[])
    add('Sedmični pregledi',[(r['week'], 'Aktivnosti: '+', '.join(clean(a.get('title'))+' ('+clean(a.get('status'))+')' for a in r.get('activities',[]))+'; KPI: '+', '.join(clean(k.get('name'))+' = '+clean(k.get('value'))+' / '+clean(k.get('period')) for k in r.get('kpi_measurements',[]))+'; Prepreke: '+', '.join(r.get('blockers',[]))+'; Odluke: '+', '.join(r.get('decisions',[]))+'; Napomena: '+clean(r.get('note'))) for r in reviews] or [('Stanje','Nema sedmičnih pregleda')])
    effects=data.get('effects',[]); sm=summarize(effects)
    add('Registar ostvarenih efekata',[(f"{e['period']} — {e['name']}",f"{e['amount_km']} KM; kategorija: {e['category']}; konsultant potvrdio: {clean(e['consultant_confirmed'])}; dokaz: {e['evidence_reference']}; obračun: {e['calculation_note']}; vlasnik izvora: {e['source_owner']}") for e in effects] or [('Stanje','Nema evidentiranih efekata')])
    add('Status potvrde efekata',[('Konsultantski potvrđeni efekti po unesenim periodima (ne godišnji)',str(sm['consultant_confirmed_recurring_km'])+' KM'),('Jednokratni obrtni kapital',str(sm['consultant_confirmed_one_time_working_capital_km'])+' KM'),('Nezavisno verificirano','0 KM'),('Nepotvrđeni unosi',sm['pending_count']),('Ograničenje',sm['warning'])])
    return sections

def export_docx(data):
    doc=Document(); sec=doc.sections[0]; sec.header.paragraphs[0].text='MEVAN 4.0 | Konsultantski izvještaj'
    if data['charter'].get('report_mode')=='demo':
        sec.header.paragraphs[0].text=DEMO_LABEL;sec.footer.paragraphs[0].text=DEMO_LABEL+' — nije stvarni provjereni nalaz'
    doc.add_heading('Izvještaj o operativnom projektu',0);doc.add_paragraph(data['title']);doc.add_paragraph('Izvoz: '+datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC'))
    doc.add_paragraph('RADNI IZVJEŠTAJ — procjene nisu potvrđeni rezultati; konsultantska potvrda nije nezavisna verifikacija.')
    for title,items in build_sections(data):
        doc.add_heading(title,level=1)
        for k,v in items:
            p=doc.add_paragraph(style='Normal');p.add_run(k+': ').bold=True;p.add_run(v)
    buf=BytesIO();doc.save(buf);return buf.getvalue()

def export_pdf(data):
    pdfmetrics.registerFont(TTFont('DejaVuMEVAN',FONT))
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='MevanTitle',fontName='DejaVuMEVAN',fontSize=15,leading=21,spaceAfter=12));styles.add(ParagraphStyle(name='MevanHead',fontName='DejaVuMEVAN',fontSize=11,leading=16,spaceBefore=13,spaceAfter=7));styles.add(ParagraphStyle(name='MevanBody',fontName='DejaVuMEVAN',fontSize=8.5,leading=13,spaceAfter=6,wordWrap='CJK'))
    story=[Paragraph('MEVAN 4.0 — Izvještaj o operativnom projektu',styles['MevanTitle']),Paragraph(escape(data['title']),styles['MevanHead']),Paragraph('RADNI IZVJEŠTAJ — procjene nisu potvrđeni rezultati. Konsultantska potvrda nije nezavisna verifikacija.',styles['MevanBody'])]
    for title,items in build_sections(data):
        story.append(Paragraph(escape(title),styles['MevanHead']))
        for k,v in items:
            story.append(Paragraph('<b>'+escape(k)+'</b>: '+escape(v).replace('\n','<br/>'),styles['MevanBody']))
    def footer(canvas,doc):
        if data['charter'].get('report_mode')=='demo':
            canvas.setFont('DejaVuMEVAN',9);canvas.drawString(36,20,DEMO_LABEL+' — nije stvarni provjereni nalaz')
    buf=BytesIO();SimpleDocTemplate(buf,pagesize=(595,842),rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=42,title='MEVAN projektni izvještaj').build(story,onFirstPage=footer,onLaterPages=footer)
    return buf.getvalue()
