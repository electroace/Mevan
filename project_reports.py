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

from mevan_report_fonts import FALLBACK as FONT, register_pdf_fonts

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

WORKING_NOTE='RADNI IZVJEŠTAJ — procjene nisu potvrđeni rezultati; konsultantska potvrda nije nezavisna verifikacija.'
DEMO_FOOTER=DEMO_LABEL+' — nije stvarni provjereni nalaz'


def export_docx(data):
    # Izgled je isti kao kod zaključanih izvještaja; uvoz je ovdje da moduli ostanu nezavisni pri pokretanju.
    from docx.enum.text import WD_TAB_ALIGNMENT
    from docx.shared import Inches, Mm
    from approved_reports import AMBER, AMBER_BG, LINE, MUTED, NAVY, SANS, TEAL, _border, _page_field, _rgb, _shade, docx_styles
    demo=data['charter'].get('report_mode')=='demo'
    doc=Document(); sec=doc.sections[0]
    sec.page_width,sec.page_height=Mm(210),Mm(297)
    sec.left_margin=sec.right_margin=Mm(22);sec.top_margin,sec.bottom_margin=Mm(24),Mm(22)
    docx_styles(doc)
    header,footer=sec.header.paragraphs[0],sec.footer.paragraphs[0]
    header.text=DEMO_LABEL if demo else 'MEVAN 4.0 | Konsultantski izvještaj'
    footer.text=DEMO_FOOTER if demo else str(data['title'])
    for inherited in (Inches(3.25),Inches(6.5)):footer.paragraph_format.tab_stops.add_tab_stop(inherited,WD_TAB_ALIGNMENT.CLEAR)
    footer.paragraph_format.tab_stops.add_tab_stop(sec.page_width-sec.left_margin-sec.right_margin,WD_TAB_ALIGNMENT.RIGHT)
    footer.add_run('\tStrana ');_page_field(footer)
    for paragraph in (header,footer):
        for run in paragraph.runs:run.font.size,run.font.name,run.font.color.rgb=Pt(8),SANS,_rgb(AMBER if demo else MUTED)
    _border(header,'bottom',NAVY,size=8,space=6)
    doc.add_heading('Izvještaj o operativnom projektu',0)
    title=doc.add_paragraph(data['title']);title.runs[0].font.size,title.runs[0].font.bold,title.runs[0].font.color.rgb=Pt(13),True,_rgb(NAVY)
    stamp=doc.add_paragraph('Izvoz: '+datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC'));stamp.runs[0].font.size,stamp.runs[0].font.color.rgb=Pt(9),_rgb(MUTED)
    note=doc.add_paragraph(WORKING_NOTE);note.runs[0].font.size,note.runs[0].font.color.rgb=Pt(9.5),_rgb(AMBER)
    _shade(note,AMBER_BG);_border(note,'left',AMBER,size=18,space=8)
    for number,(title,items) in enumerate(build_sections(data),1):
        heading=doc.add_heading(level=1)
        mark=heading.add_run(f'{number:02d}   ');mark.font.name,mark.font.size,mark.font.color.rgb=SANS,Pt(9),_rgb(TEAL)
        heading.add_run(title);_border(heading,'top',LINE,space=8)
        for k,v in items:
            p=doc.add_paragraph(style='Normal');p.paragraph_format.space_after=Pt(5)
            label=p.add_run(k+': ');label.bold=True;label.font.color.rgb=_rgb(NAVY);p.add_run(v)
    buf=BytesIO();doc.save(buf);return buf.getvalue()

def export_pdf(data):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from approved_reports import AMBER, AMBER_BG, INK, MUTED, NAVY, TEAL, _numbered_canvas
    fonts=register_pdf_fonts();demo=data['charter'].get('report_mode')=='demo'
    def style(name,role='body',size=10,leading=None,color=INK,**extra):
        return ParagraphStyle(name,fontName=fonts[role],fontSize=size,leading=leading or size*1.42,textColor=colors.HexColor(color),**extra)
    kicker=style('p-kicker','bold',8,color=TEAL,spaceAfter=5)
    title=style('p-title','display',23,27,NAVY,spaceAfter=4)
    stamp=style('p-stamp',size=9,color=MUTED,spaceAfter=4)
    notice=style('p-notice',size=9,leading=12.5,color=AMBER,backColor=colors.HexColor(AMBER_BG),borderPadding=(6,8,6,8),spaceBefore=10,spaceAfter=6,leftIndent=8,rightIndent=8)
    head=style('p-head','display',14,17.5,NAVY,spaceBefore=18,spaceAfter=6,keepWithNext=1)
    label=style('p-label','bold',8,10.5,MUTED,spaceBefore=5,keepWithNext=1)
    body=style('p-body',size=9.5,leading=13.6,spaceAfter=2)
    story=[Paragraph('MEVAN 4.0 — IZVJEŠTAJ O OPERATIVNOM PROJEKTU',kicker),Paragraph(escape(data['title']),title),
           Paragraph('Izvoz: '+datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC'),stamp),
           Paragraph('RADNI IZVJEŠTAJ — procjene nisu potvrđeni rezultati. Konsultantska potvrda nije nezavisna verifikacija.',notice)]
    for number,(section,items) in enumerate(build_sections(data),1):
        story.append(Paragraph(f'<font name="{fonts["bold"]}" size="8.5" color="{TEAL}">{number:02d}</font>&nbsp;&nbsp;&nbsp;{escape(section)}',head))
        for k,v in items:
            story+=[Paragraph(escape(k),label),Paragraph(escape(v).replace('\n','<br/>'),body)]
    furniture=_numbered_canvas({'demo':demo,'kind':'Izvještaj o operativnom projektu','company':str(data['title'])},fonts)
    buf=BytesIO()
    # Okvir strane ima 6 pt unutrašnjeg razmaka; margine ga uračunavaju.
    SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm-6,rightMargin=20*mm-6,topMargin=24*mm-6,bottomMargin=22*mm-6,title='MEVAN projektni izvještaj').build(story,canvasmaker=furniture)
    return buf.getvalue()
