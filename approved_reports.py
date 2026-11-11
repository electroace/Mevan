"""Two report views derived from the same approved diagnostic snapshot."""
from io import BytesIO
from datetime import datetime, timezone
import re
import unicodedata
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from mevan_report_fonts import font_paths, register_pdf_fonts
from diagnostic_engine import DIMENSIONS, analyze
from mevan_test_approval import ApprovalError, read_approval
from mevan_test_report_manifest import prepare_report_manifest
from mevan_report_model import DEMO_LABEL

PERIODS = ("1–30 dana", "31–60 dana", "61–90 dana")


REVIEW_FIELDS = {
    'summary': ('Izvršni sažetak', 80, 12),
    'priority1': ('Prvi prioritet', 40, 6),
    'priority2': ('Drugi prioritet', 40, 6),
    'priority3': ('Treći prioritet', 40, 6),
    'month1': ('Plan za 1–30 dana', 60, 10),
    'month2': ('Plan za 31–60 dana', 60, 10),
    'month3': ('Plan za 61–90 dana', 60, 10),
}


def validate_review(diagnostic, *, for_approval=False):
    """Technical completeness only, never a professional assessment of quality.

    Stricter rules apply to NEW approvals, not historical snapshot downloads.
    """
    review = diagnostic.get("consultant_review", {})
    if not isinstance(review, dict) or any(not isinstance(review.get(k), str) or not review[k].strip() for k in REVIEW_FIELDS):
        raise ApprovalError("Dopunite sažetak, tri prioriteta i sva tri perioda plana.")
    if for_approval:
        errors = []
        placeholders = {'x', 'xx', 'xxx', 'test', 'tekst', 'placeholder', 'tbd', 'todo',
                        'naknadno', 'dopuniti', 'sazetak', 'prioritet', 'plan', 'nije', 'uneseno',
                        'nema', 'podataka', 'primjer', 'lorem', 'ipsum', 'dolor', 'sit', 'amet'}
        for key, (label, min_chars, min_words) in REVIEW_FIELDS.items():
            value = ' '.join(review[key].split())
            words = re.findall(r'[^\W\d_]+', value.casefold(), flags=re.UNICODE)
            tokens = {''.join(c for c in unicodedata.normalize('NFKD', w) if not unicodedata.combining(c)) for w in words}
            if (len(value) < min_chars or len(words) < min_words or len(tokens) < 4
                    or tokens <= placeholders or len(value) > 6000):
                errors.append(f'{label}: unesite konkretan tekst ({min_chars}–6000 znakova i najmanje {min_words} riječi), bez zamjenskih oznaka i ponavljanja.')
        if errors:
            raise ApprovalError(' '.join(errors) + ' Ovo je tehnička provjera potpunosti; stručni pregled sadržaja ostaje obaveza konsultanta.')
    return review


def report_content(db, approval_id, view):
    """Sadržaj izvještaja iz zaključanog snimka. Izgled određuju render funkcije ispod."""
    approval = read_approval(db, approval_id)
    ci, di = approval["company_index"], approval["diagnostic_index"]
    prepare_report_manifest(db, approval_id, ci, di)
    company = approval["workspace"]["companies"][ci]
    diagnostic = company["diagnostics"][di]
    review = validate_review(diagnostic)
    records = sorted(diagnostic["quality_records"], key=lambda row: row["criterion_id"])
    modern = approval['policy_version'] == 2
    demo = approval['report_mode'] == 'demo'
    assessment = {r["criterion_id"]: {"score": r["score"], "proof": "confirmed",
                  "evidence": r.get("evidence_reference", "")} for r in records}
    result = approval['report_model']['result'] if modern else analyze({"assess": assessment, "effects": diagnostic.get("effects", [])})
    guided = diagnostic.get('guided', {})
    na = [r for r in records if r['verification_status'] == 'nije_primjenjivo'] if modern else []
    dimensions = []
    for code, name in DIMENSIONS.items():
        dim = result['dimensions'][code]
        dimensions.append({'name': name, 'index': dim['index'],
                           'scope': f'primjenjivo {dim["applicable"]}, N/P {dim["na"]}' if modern else ''})
    scenarios = []
    for item in result["finance"]["excluded"]:
        amount = (f'{item["oneoff"]} KM jednokratno' if item["category"] == "working_capital"
                  else f'{item["annual"]} KM godišnje')
        scenarios.append({'name': str(item["name"]), 'amount': amount, 'reason': str(item["reason"])})
    criteria = []
    if view == "detailed":
        for r in records:
            code = r["criterion_id"]
            collection = [(label, r.get('collection', {}).get(source, ''))
                          for source, label in (('interview', 'Intervju'), ('documents', 'Dokumenti'), ('visit', 'Obilazak'))]
            if modern and r['verification_status'] == 'nije_primjenjivo':
                criteria.append({'code': code, 'name': r.get("criterion_name", ""), 'score': None,
                                 'collection': [(label, str(note)) for label, note in collection if note]})
                continue
            criteria.append({
                'code': code, 'name': r.get("criterion_name", ""), 'score': r["score"],
                'evidence': str(r["evidence_reference"]),
                'source': f'Izvor {r.get("source_id", "simulacija" if demo else "")} · Period {r.get("reference_period_start", "—")} – {r.get("reference_period_end", "—")}',
                'trace': f'{"Simulirani procjenjivač" if demo else "Procijenio"} {r.get("assessor_id", "DEMO")} · Trag {r.get("verification_audit_ref", "simulirani podaci")}',
                'collection': [(label, str(note) if note else 'Nije prikupljeno') for label, note in collection] if modern else [],
                'finding': str(diagnostic.get("assess", {}).get(code, {}).get("finding") or ''),
            })
    return {
        'demo': demo, 'modern': modern, 'view': view,
        'kind': "Direktorski izvještaj" if view == "executive" else "Detaljni stručni izvještaj",
        'company': company.get("company", {}).get("name") or company.get("id", ""),
        'diagnostic': f'{diagnostic.get("name", "")} · ID {approval["diagnostic_id"]}',
        'meta': [("DEMO snimak" if demo else "Odobrenje", str(approval_id)),
                 ("Revizija", str(approval["workspace_revision"])),
                 ("Pripremio" if demo else "Konsultant", str(approval["reviewer_id"]))]
                + ([("Zaključano (UTC)", datetime.fromtimestamp(approval["approved_at"], timezone.utc).strftime('%d.%m.%Y. %H:%M'))] if modern else []),
        'summary': review["summary"],
        'priorities': [review[f"priority{i}"] for i in range(1, 4)],
        'selection': f'Odabrani prioritet: {guided.get("selected_candidate", "Nije odabran")} · Projektni nacrt: {guided.get("project_id", "Nije povezan")}' if modern else '',
        'selected': {'C1': 0, 'C2': 1, 'C3': 2}.get(guided.get("selected_candidate")) if modern else None,
        'index': result["index"], 'criteria_count': len(records),
        'scope': f'Primjenjivo {61 - len(na)}/61 · N/P {len(na)}. N/P je isključen iz nazivnika; nepoznato nije ocjena nula.' if modern else '',
        'dimensions': dimensions,
        'not_applicable': [f'{row["criterion_id"]} · N/P · {row["na_reason"]} · Potvrdio konsultant: {row["na_approved_by"]}' for row in na],
        'scenarios': scenarios,
        'plan': [(period, review[f"month{i}"]) for i, period in enumerate(PERIODS, 1)],
        'criteria': criteria,
        'sha256': approval["sha256"],
    }


DEMO_NOTICE = DEMO_LABEL + ' — nije stvarno konsultantsko odobrenje, provjera dokaza ili potvrda finansijskog efekta.'
DEMO_FOOTER = DEMO_LABEL + ' — nije stvarni provjereni nalaz'
INK, NAVY, TEAL, MUTED, LINE, SOFT, AMBER, AMBER_BG = '#1b2a38', '#142e46', '#0a6485', '#566b7c', '#d5dde4', '#eef2f5', '#8a4d00', '#fdf3df'


def index_text(value):
    return 'Neocjenjivo' if value is None else str(value)


def overall_text(content):
    if content['index'] is None:
        return 'Neocjenjivo — nema ocijenjenih primjenjivih kriterija' + f' · {content["criteria_count"]} kriterija'
    return f'Ukupni indeks {content["index"]}/100 · {content["criteria_count"]} kriterija'


def chart_png(content):
    """Trake zrelosti po oblastima za Word. Neocjenjiva oblast nema traku i nije nula."""
    from PIL import Image, ImageDraw, ImageFont
    fonts = font_paths()
    label_font, value_font, small_font = (ImageFont.truetype(fonts[role], size) for role, size in (('body', 30), ('bold', 30), ('body', 22)))
    row, left, right, width = 92, 300, 150, 1400
    picture = Image.new('RGB', (width, row * len(content['dimensions']) + 46), 'white')
    draw = ImageDraw.Draw(picture)
    track = width - left - right
    for position, dim in enumerate(content['dimensions']):
        top = position * row + 14
        draw.text((0, top + 6), dim['name'], fill=INK, font=label_font)
        if dim['scope']:
            draw.text((0, top + 44), dim['scope'], fill=MUTED, font=small_font)
        if dim['index'] is None:
            draw.text((left, top + 6), 'Neocjenjivo', fill=MUTED, font=label_font)
            continue
        draw.rectangle((left, top + 14, left + track, top + 38), fill=SOFT)
        draw.rectangle((left, top + 14, left + track * max(0, min(100, dim['index'])) / 100, top + 38), fill=TEAL)
        draw.text((width, top + 6), str(dim['index']), fill=INK, font=value_font, anchor='ra')
    base = row * len(content['dimensions']) + 8
    for mark in (0, 50, 100):
        x = left + track * mark / 100
        draw.line((x, base, x, base + 8), fill=LINE, width=2)
        draw.text((x, base + 12), str(mark), fill=MUTED, font=small_font, anchor='ma')
    output = BytesIO()
    picture.save(output, format='PNG')
    output.seek(0)
    return output


# ---- PDF

class MaturityBars(Flowable):
    """Vektorske trake zrelosti; vrijednost je uvijek ispisana i kao tekst."""

    def __init__(self, dimensions, width, fonts):
        super().__init__()
        self.dimensions, self.width, self.fonts = dimensions, width, fonts
        self.row = 9.2 * mm
        self.height = self.row * len(dimensions) + 6 * mm

    def draw(self):
        c, label_w, value_w = self.canv, 34 * mm, 15 * mm
        track = self.width - label_w - value_w
        for position, dim in enumerate(self.dimensions):
            y = self.height - (position + 1) * self.row + 3.4 * mm
            c.setFillColor(colors.HexColor(INK)); c.setFont(self.fonts['body'], 9.5)
            c.drawString(0, y + (1.6 * mm if dim['scope'] else 0), dim['name'])
            if dim['scope']:
                c.setFillColor(colors.HexColor(MUTED)); c.setFont(self.fonts['body'], 7)
                c.drawString(0, y - 1.7 * mm, dim['scope'])
            if dim['index'] is None:
                c.setFillColor(colors.HexColor(MUTED)); c.setFont(self.fonts['body'], 9.5)
                c.drawString(label_w, y, 'Neocjenjivo')
                continue
            c.setFillColor(colors.HexColor(SOFT)); c.rect(label_w, y - .2 * mm, track, 2.6 * mm, stroke=0, fill=1)
            c.setFillColor(colors.HexColor(TEAL))
            c.rect(label_w, y - .2 * mm, track * max(0, min(100, dim['index'])) / 100, 2.6 * mm, stroke=0, fill=1)
            c.setFillColor(colors.HexColor(INK)); c.setFont(self.fonts['bold'], 9.5)
            c.drawRightString(self.width, y, str(dim['index']))
        c.setStrokeColor(colors.HexColor(LINE)); c.setLineWidth(.4)
        c.setFillColor(colors.HexColor(MUTED)); c.setFont(self.fonts['body'], 6.5)
        for mark in (0, 50, 100):
            x = label_w + track * mark / 100
            c.line(x, 4.4 * mm, x, 5.4 * mm)
            c.drawCentredString(x, 1.6 * mm, str(mark))


class ScorePips(Flowable):
    """Ocjena 0–5 kao pet polja uz ispisanu vrijednost."""

    def __init__(self, score, fonts):
        super().__init__()
        self.score, self.fonts, self.width, self.height = score, fonts, 34 * mm, 4.2 * mm

    def draw(self):
        c = self.canv
        c.setFont(self.fonts['bold'], 9.5); c.setFillColor(colors.HexColor(INK if self.score is not None else MUTED))
        c.drawRightString(self.width, .6 * mm, 'N/P' if self.score is None else f'{self.score}/5')
        if self.score is None:
            return
        try:
            filled = max(0, min(5, int(round(float(self.score)))))
        except (TypeError, ValueError):
            return
        for position in range(5):
            c.setFillColor(colors.HexColor(TEAL if position < filled else LINE))
            c.rect(position * 4.1 * mm, .7 * mm, 3.4 * mm, 2.2 * mm, stroke=0, fill=1)


def _numbered_canvas(content, fonts):
    """Zaglavlje i podnožje svake strane; ukupan broj strana poznat je tek na kraju."""
    kind = (DEMO_LABEL + ' · ' if content['demo'] else '') + content['kind']

    class ReportCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for state in self._pages:
                self.__dict__.update(state)
                self._furniture(total)
                super().showPage()
            super().save()

        def _furniture(self, total):
            width, height = A4
            left, right = 20 * mm, width - 20 * mm
            self.saveState()
            self.setFillColor(colors.HexColor(NAVY)); self.setFont(fonts['bold'], 9)
            self.drawString(left, height - 13 * mm, 'MEVAN', charSpace=1.6)
            self.setFont(fonts['body'], 7.5); self.setFillColor(colors.HexColor(MUTED))
            self.drawString(left + 17 * mm, height - 13 * mm, 'DIAGNOSTIC', charSpace=.8)
            self.drawRightString(right, height - 13 * mm, kind)
            self.setStrokeColor(colors.HexColor(NAVY)); self.setLineWidth(.9)
            self.line(left, height - 15.5 * mm, right, height - 15.5 * mm)
            self.setStrokeColor(colors.HexColor(LINE)); self.setLineWidth(.4)
            self.line(left, 15 * mm, right, 15 * mm)
            self.setFont(fonts['body'], 7.5)
            if content['demo']:
                self.setFillColor(colors.HexColor(AMBER)); self.drawString(left, 10.5 * mm, DEMO_FOOTER)
            else:
                self.setFillColor(colors.HexColor(MUTED)); self.drawString(left, 10.5 * mm, content['company'][:80])
            self.setFillColor(colors.HexColor(MUTED))
            self.drawRightString(right, 10.5 * mm, f'Strana {self._pageNumber} / {total}')
            self.restoreState()

    return ReportCanvas


def render_pdf(content):
    fonts = register_pdf_fonts()
    def style(name, role='body', size=10, leading=None, color=INK, **extra):
        return ParagraphStyle(name, fontName=fonts[role], fontSize=size, leading=leading or size * 1.42,
                              textColor=colors.HexColor(color), **extra)
    s = {
        'kicker': style('kicker', 'bold', 8, color=TEAL, spaceAfter=5),
        'title': style('title', 'display', 25, 29, NAVY, spaceAfter=3),
        'subtitle': style('subtitle', size=11, color=MUTED, spaceAfter=10),
        'label': style('label', size=7, leading=9, color=MUTED),
        'value': style('value', 'bold', 9.5, 12.5),
        'notice': style('notice', size=9, leading=12.5, color=AMBER, backColor=colors.HexColor(AMBER_BG), borderPadding=(6, 8, 6, 8), spaceBefore=12, spaceAfter=6, leftIndent=8, rightIndent=8),
        'section': style('section', 'display', 14.5, 18, NAVY, spaceBefore=18, spaceAfter=7, keepWithNext=1),
        'body': style('body', size=10, leading=14.6, spaceAfter=6),
        'priority': style('priority', size=10, leading=14.6, spaceAfter=7, leftIndent=11 * mm, bulletIndent=0, bulletFontName=fonts['display'], bulletFontSize=17, bulletColor=colors.HexColor(TEAL), bulletOffsetY=-3),
        'tag': style('tag', 'bold', 7, 9, TEAL, leftIndent=11 * mm, spaceAfter=1),
        'small': style('small', size=8.2, leading=11.4, color=MUTED, spaceAfter=3),
        'period': style('period', 'bold', 9.5, 12, TEAL, spaceBefore=8, spaceAfter=2, keepWithNext=1),
        'big': style('big', 'display', 34, 36, NAVY),
        'group': style('group', 'bold', 8, 10, MUTED, spaceBefore=14, spaceAfter=2, keepWithNext=1),
        'criterion': style('criterion', 'bold', 10.2, 13.5, NAVY),
        'cell': style('cell', size=9, leading=12.4),
        'cellbold': style('cellbold', 'bold', 9, 12.4),
        'head': style('head', 'bold', 7.5, 10, MUTED),
        'hash': style('hash', size=7, leading=9.5, color=MUTED, spaceBefore=16),
    }
    def text(value, name='body'):
        return Paragraph(escape(str(value)).replace("\n", "<br/>"), s[name])
    counter = iter(range(1, 20))
    def section(title):
        return Paragraph(f'<font name="{fonts["bold"]}" size="8.5" color="{TEAL}">{next(counter):02d}</font>&nbsp;&nbsp;&nbsp;{escape(title)}', s['section'])
    page_width = A4[0] - 40 * mm
    hairline = lambda: Table([['']], colWidths=[page_width], rowHeights=[.1], style=TableStyle([('LINEABOVE', (0, 0), (-1, 0), .4, colors.HexColor(LINE))]))

    story = [text(content['kind'].upper(), 'kicker'), text(content['company'], 'title'), text(content['diagnostic'], 'subtitle')]
    meta = content['meta']
    story.append(Table([[text(label.upper(), 'label') for label, _ in meta], [text(value, 'value') for _, value in meta]],
                       colWidths=[page_width / len(meta)] * len(meta),
                       style=TableStyle([('LINEABOVE', (0, 0), (-1, 0), .4, colors.HexColor(LINE)), ('LINEBELOW', (0, 1), (-1, 1), .4, colors.HexColor(LINE)),
                                         ('TOPPADDING', (0, 0), (-1, 0), 7), ('BOTTOMPADDING', (0, 0), (-1, 0), 1), ('TOPPADDING', (0, 1), (-1, 1), 0),
                                         ('BOTTOMPADDING', (0, 1), (-1, 1), 7), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 8), ('VALIGN', (0, 0), (-1, -1), 'TOP')])))
    if content['demo']:
        story.append(text(DEMO_NOTICE, 'notice'))

    story += [section('Sažetak konsultanta'), text(content['summary'])]

    story.append(section('Tri prioriteta'))
    for position, priority in enumerate(content['priorities']):
        if position == content['selected']:
            story.append(text('ODABRAN ZA PROJEKAT', 'tag'))
        story.append(Paragraph(escape(priority).replace("\n", "<br/>"), s['priority'], bulletText=str(position + 1)))
    if content['selection']:
        story.append(text(content['selection'], 'small'))

    story.append(section('Zrelost po oblastima'))
    left = [text(index_text(content['index']) if content['index'] is not None else '—', 'big'), Spacer(1, 4), text(overall_text(content), 'small')]
    if content['scope']:
        left.append(text(content['scope'], 'small'))
    story.append(Table([[left, MaturityBars(content['dimensions'], page_width - 62 * mm, fonts)]], colWidths=[62 * mm, page_width - 62 * mm],
                       style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (0, 0), 10),
                                         ('RIGHTPADDING', (1, 0), (1, 0), 0), ('LEFTPADDING', (1, 0), (1, 0), 0), ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)])))

    if content['not_applicable']:
        story.append(section('Nije primjenjivo — obuhvat i razlozi'))
        story += [text(row) for row in content['not_applicable']]

    story.append(section('Finansijski potencijal'))
    if content['scenarios']:
        rows = [[text('SCENARIJ', 'head'), text('PROCJENA', 'head'), text('NAPOMENA', 'head')]]
        rows += [[text(item['name'], 'cellbold'), text('procjena ' + item['amount'], 'cell'), text(item['reason'], 'cell')] for item in content['scenarios']]
        story.append(Table(rows, colWidths=[52 * mm, 40 * mm, page_width - 92 * mm], repeatRows=1,
                           style=TableStyle([('LINEBELOW', (0, 0), (-1, 0), .7, colors.HexColor(NAVY)), ('LINEBELOW', (0, 1), (-1, -1), .4, colors.HexColor(LINE)),
                                             ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                                             ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)])))
    else:
        story.append(text('Nije evidentiran finansijski scenario.'))

    story.append(section('Plan za 90 dana'))
    for period, plan in content['plan']:
        story += [text(period, 'period'), text(plan)]

    if content['criteria']:
        story.append(section('Ocjene i trag provjere dokaza'))
        group = None
        for item in content['criteria']:
            if item['code'][:1] != group:
                group = item['code'][:1]
                story.append(text(DIMENSIONS.get(group, group).upper(), 'group'))
            title = f'{item["code"]} · {item["name"]}' + (' · N/P (isključeno iz obračuna)' if item['score'] is None else '')
            story.append(Table([[text(title, 'criterion'), ScorePips(item['score'], fonts)]], colWidths=[page_width - 36 * mm, 36 * mm],
                               style=TableStyle([('LINEABOVE', (0, 0), (-1, 0), .4, colors.HexColor(LINE)), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                 ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)])))
            if item['score'] is not None:
                story += [text(item['evidence'], 'cell'), Spacer(1, 2), text(item['source'], 'small'), text(item['trace'], 'small')]
            for label, note in item['collection']:
                story.append(Paragraph(f'<font name="{fonts["bold"]}">{label}:</font> {escape(note)}'.replace("\n", "<br/>"), s['cell']))
            if item.get('finding'):
                story += [Spacer(1, 3), text(item['finding'], 'cell')]
            story.append(Spacer(1, 6))

    story += [hairline(), text('SHA-256 zaključanog snimka: ' + content['sha256'], 'hash')]
    buffer = BytesIO()
    # Okvir strane ima 6 pt unutrašnjeg razmaka; margine ga uračunavaju da tekst i tabele stoje u istoj liniji.
    SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20 * mm - 6, rightMargin=20 * mm - 6, topMargin=24 * mm - 6, bottomMargin=22 * mm - 6,
                      title=(DEMO_LABEL + ' · ' if content['demo'] else '') + content['kind'], author='MEVAN Diagnostic').build(story, canvasmaker=_numbered_canvas(content, fonts))
    return buffer.getvalue()


# ---- Word

SANS, SERIF = 'Calibri', 'Georgia'


def _rgb(colour):
    return RGBColor.from_string(colour.lstrip('#').upper())


def _border(paragraph, side, colour, size=6, space=4):
    properties = paragraph._p.get_or_add_pPr()
    borders = properties.find(qn('w:pBdr'))
    if borders is None:
        borders = OxmlElement('w:pBdr')
        properties.append(borders)
    edge = OxmlElement('w:' + side)
    for key, value in (('val', 'single'), ('sz', str(size)), ('space', str(space)), ('color', colour.lstrip('#'))):
        edge.set(qn('w:' + key), value)
    borders.append(edge)


def _shade(paragraph, colour):
    shading = OxmlElement('w:shd')
    for key, value in (('val', 'clear'), ('color', 'auto'), ('fill', colour.lstrip('#'))):
        shading.set(qn('w:' + key), value)
    paragraph._p.get_or_add_pPr().append(shading)


def _page_field(paragraph):
    run = paragraph.add_run()
    for kind, instruction in (('begin', None), (None, 'PAGE'), ('end', None)):
        if kind:
            mark = OxmlElement('w:fldChar'); mark.set(qn('w:fldCharType'), kind); run._r.append(mark)
        else:
            code = OxmlElement('w:instrText'); code.set(qn('xml:space'), 'preserve'); code.text = instruction; run._r.append(code)
    return run


def render_docx(content):
    document = Document()
    page = document.sections[0]
    page.page_width, page.page_height = Mm(210), Mm(297)
    page.left_margin = page.right_margin = Mm(22)
    page.top_margin, page.bottom_margin = Mm(24), Mm(22)
    text_width = page.page_width - page.left_margin - page.right_margin

    def restyle(name, font, size, colour, bold=False, before=0, after=6, line=1.25, keep=False):
        style = document.styles[name]
        style.font.name, style.font.size, style.font.bold, style.font.italic = font, Pt(size), bold, False
        style.font.color.rgb = _rgb(colour)
        style.element.rPr.rFonts.set(qn('w:eastAsia'), font)
        for theme in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
            style.element.rPr.rFonts.attrib.pop(qn('w:' + theme), None)
        layout = style.paragraph_format
        layout.space_before, layout.space_after, layout.line_spacing, layout.keep_with_next = Pt(before), Pt(after), line, keep
        return style
    restyle('Normal', SANS, 10.5, INK, line=1.3)
    restyle('Body Text', SANS, 10.5, INK, line=1.3)
    restyle('Title', SERIF, 25, NAVY, bold=True, after=2, line=1.1)
    restyle('Heading 1', SERIF, 15, NAVY, bold=True, before=20, after=7, line=1.15, keep=True)
    restyle('Heading 2', SANS, 10.5, TEAL, bold=True, before=9, after=2, keep=True)
    restyle('Heading 3', SANS, 10.5, NAVY, bold=True, before=11, after=2, keep=True)
    for name in ('Title',):
        borders = document.styles[name].element.pPr.find(qn('w:pBdr'))
        if borders is not None:
            document.styles[name].element.pPr.remove(borders)

    def add(value, style='Body Text', size=None, colour=None, bold=None, after=None):
        paragraph = document.add_paragraph(style=style)
        run = paragraph.add_run(str(value))
        if size: run.font.size = Pt(size)
        if colour: run.font.color.rgb = _rgb(colour)
        if bold is not None: run.font.bold = bold
        if after is not None: paragraph.paragraph_format.space_after = Pt(after)
        return paragraph
    counter = iter(range(1, 20))
    def section(title):
        paragraph = document.add_paragraph(style='Heading 1')
        number = paragraph.add_run(f'{next(counter):02d}   ')
        number.font.name, number.font.size, number.font.color.rgb = SANS, Pt(9), _rgb(TEAL)
        paragraph.add_run(title)
        _border(paragraph, 'top', LINE, space=8)
        return paragraph

    header = page.header.paragraphs[0]
    header.text = DEMO_LABEL if content['demo'] else "MEVAN  /  Dijagnostika"
    footer = page.footer.paragraphs[0]
    footer.text = DEMO_FOOTER if content['demo'] else content['company']
    for inherited in (Inches(3), Inches(6)):  # zadani graničnici stila podnožja
        footer.paragraph_format.tab_stops.add_tab_stop(inherited, WD_TAB_ALIGNMENT.CLEAR)
    footer.paragraph_format.tab_stops.add_tab_stop(text_width, WD_TAB_ALIGNMENT.RIGHT)
    footer.add_run('\tStrana ')
    _page_field(footer)
    for paragraph, colour in ((header, AMBER if content['demo'] else MUTED), (footer, AMBER if content['demo'] else MUTED)):
        for run in paragraph.runs:
            run.font.size, run.font.name, run.font.color.rgb = Pt(8), SANS, _rgb(colour)
    _border(header, 'bottom', NAVY, size=8, space=6)

    add(content['kind'].upper(), size=8.5, colour=TEAL, bold=True, after=4)
    document.add_paragraph(content['company'], style='Title')
    add(content['diagnostic'], size=11.5, colour=MUTED, after=10)
    for position, (label, value) in enumerate(content['meta']):
        paragraph = document.add_paragraph(style='Body Text')
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.paragraph_format.tab_stops.add_tab_stop(Mm(52))
        name = paragraph.add_run(label + ' ')
        name.font.size, name.font.color.rgb = Pt(9), _rgb(MUTED)
        detail = paragraph.add_run('\t' + value)
        detail.font.bold = True
        if position == 0:
            _border(paragraph, 'top', LINE, space=6)
    if content['demo']:
        notice = add(DEMO_NOTICE, size=9.5, colour=AMBER)
        notice.paragraph_format.space_before = Pt(12)
        _shade(notice, AMBER_BG); _border(notice, 'left', AMBER, size=18, space=8)

    section('Sažetak konsultanta')
    add(content['summary'])

    section('Tri prioriteta')
    for position, priority in enumerate(content['priorities']):
        paragraph = document.add_paragraph(style='Body Text')
        paragraph.paragraph_format.left_indent, paragraph.paragraph_format.first_line_indent = Mm(9), Mm(-9)
        paragraph.paragraph_format.tab_stops.add_tab_stop(Mm(9))
        number = paragraph.add_run(f'{position + 1}.\t')
        number.font.bold, number.font.color.rgb = True, _rgb(TEAL)
        paragraph.add_run(priority)
        if position == content['selected']:
            tag = paragraph.add_run('  — odabran za projekat')
            tag.font.size, tag.font.bold, tag.font.color.rgb = Pt(8.5), True, _rgb(TEAL)
    if content['selection']:
        add(content['selection'], size=9, colour=MUTED)

    section('Zrelost po oblastima')
    add(overall_text(content), bold=True, after=2)
    if content['scope']:
        add(content['scope'], size=9, colour=MUTED)
    for dim in content['dimensions']:
        paragraph = document.add_paragraph(style='Body Text')
        paragraph.paragraph_format.space_after = Pt(1)
        value = f'{dim["index"]}/100' if dim['index'] is not None else 'Neocjenjivo'
        paragraph.add_run(f'{dim["name"]} · {value}')
        if dim['scope']:
            scope = paragraph.add_run(' · ' + dim['scope'])
            scope.font.size, scope.font.color.rgb = Pt(9), _rgb(MUTED)
    chart = document.add_paragraph()
    chart.paragraph_format.space_before = Pt(8)
    chart.add_run().add_picture(chart_png(content), width=Mm(150))

    if content['not_applicable']:
        section('Nije primjenjivo — obuhvat i razlozi')
        for row in content['not_applicable']:
            add(row)

    section('Finansijski potencijal')
    if not content['scenarios']:
        add('Nije evidentiran finansijski scenario.')
    for item in content['scenarios']:
        paragraph = document.add_paragraph(style='Body Text')
        paragraph.add_run(item['name']).font.bold = True
        paragraph.add_run(f' · procjena {item["amount"]} · {item["reason"]}')
        _border(paragraph, 'bottom', LINE, size=4, space=3)

    section('Plan za 90 dana')
    for period, plan in content['plan']:
        document.add_paragraph(period, style='Heading 2')
        add(plan)

    if content['criteria']:
        section('Ocjene i trag provjere dokaza')
        for item in content['criteria']:
            heading = f'{item["code"]} · {item["name"]} · ' + ('N/P (isključeno iz obračuna)' if item['score'] is None else f'{item["score"]}/5')
            _border(document.add_paragraph(heading, style='Heading 3'), 'top', LINE, size=4, space=5)
            if item['score'] is not None:
                add(item['evidence'], after=3)
                add(item['source'], size=9, colour=MUTED, after=1)
                add(item['trace'], size=9, colour=MUTED, after=3)
            for label, note in item['collection']:
                paragraph = document.add_paragraph(style='Body Text')
                paragraph.paragraph_format.space_after = Pt(1)
                paragraph.add_run(label + ': ').font.bold = True
                paragraph.add_run(note)
            if item.get('finding'):
                add(item['finding']).paragraph_format.space_before = Pt(4)

    add('SHA-256 zaključanog snimka: ' + content['sha256'], size=8, colour=MUTED).paragraph_format.space_before = Pt(18)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def render(db, approval_id, view, fmt):
    content = report_content(db, approval_id, view)
    return render_docx(content) if fmt == "docx" else render_pdf(content)
