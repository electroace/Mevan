"""Premium PDF izvještaj za model 65/6 (dio 6a: naslovnica, pregled, metodologija, radar, strane po modulima).

Vizuelni uzor je MEVAN_DRVONOVA_Premium_Diagnostic_v2_SIMULACIJA.pdf iz integracijskog paketa. Uzor je samo izgled:
svaki broj i tekst u ovom izvještaju dolazi iz podataka dijagnostike i iz engine-a (nalazi, pouzdanost, finansije, rang).
Izvještaj uvijek nosi oznaku nacrta metodologije i neodobrenog statusa; simulirani podaci su označeni na svakoj strani.
"""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import mevan_confidence
import mevan_finance_v2
import mevan_findings
import mevan_methodology
import mevan_projects_v2
from mevan_report_fonts import register_pdf_fonts

NAVY, TEAL, GOLD, RED, INK, MUTED, SOFT, LINE = '#10263b', '#0f7f7a', '#c8a76a', '#b5463c', '#1b2a38', '#566b7c', '#f1f4f6', '#d5dde4'
WIDTH, HEIGHT = A4
MARGIN = 20 * mm
BAND = {'HIGH': 'VISOKA', 'MEDIUM': 'SREDNJA', 'LOW': 'NISKA', 'UNKNOWN': 'NEPOZNATA'}
KIND = {'KANDIDAT_SLABOST': 'kandidat za slabost', 'PRAZNINA_U_DOKAZIMA': 'praznina u dokazima', 'DJELIMICNO_RAZVIJENO': 'djelimično razvijeno',
        'NEPOTVRDJENA_SNAGA': 'nepotvrđena snaga', 'KANDIDAT_SNAGA': 'kandidat za snagu', 'NIJE_PRIMJENJIVO': 'nije primjenjivo'}


def index_text(value):
    return 'Neocjenjivo' if value is None else f'{value:.1f}/100'


def number(value):
    return f'{value:,.0f}'.replace(',', '.')


def prepare(data):
    """Sve što izvještaj prikazuje, izračunato iz ulaza. Ovdje nema upisanih brojeva."""
    assess = data.get('assess') if isinstance(data.get('assess'), dict) else {}
    simulated = data.get('simulated') is True
    effects = data.get('effects') if isinstance(data.get('effects'), list) else []
    options = data.get('options') if isinstance(data.get('options'), list) else []
    findings = mevan_findings.build(assess, simulated)
    catalogue = mevan_methodology.load('v2')
    modules = []
    for module in catalogue['modules']:
        stats = findings['maturity']['modules'][module['code']]
        rows = [f for f in findings['findings'] if f['module'] == module['code']]
        modules.append({'code': module['code'], 'name': module['name'], 'index': stats['index'], 'verified': stats['verified'],
                        'criteria': len(rows), 'findings': rows})
    return {
        'company': str(data.get('company') or 'Kompanija')[:120], 'diagnostic': str(data.get('diagnostic') or '')[:160],
        'generated': str(data.get('generated') or '')[:40], 'simulated': simulated, 'findings': findings, 'modules': modules,
        'confidence': mevan_confidence.build(assess, effects, simulated), 'finance': mevan_finance_v2.evaluate(effects, simulated),
        'ranking': mevan_projects_v2.rank(options, assess, simulated) if options else None,
        'status': ('SIMULACIJA · ' if simulated else '') + 'NACRT METODOLOGIJE 65/6 · NEODOBRENO',
    }


class Bar(Flowable):
    """Traka 0–100 s vrijednošću. Nepoznata vrijednost nema traku i piše „Neocjenjivo”."""

    def __init__(self, label, value, note, width, fonts):
        super().__init__()
        self.label, self.value, self.note, self.width, self.fonts, self.height = label, value, note, width, fonts, 15 * mm

    def draw(self):
        c = self.canv
        c.setFont(self.fonts['bold'], 9.5); c.setFillColor(colors.HexColor(INK)); c.drawString(0, 10 * mm, self.label)
        c.setFont(self.fonts['body'], 8); c.setFillColor(colors.HexColor(MUTED)); c.drawRightString(self.width, 10 * mm, self.note)
        if self.value is None:
            c.setFont(self.fonts['body'], 8.5); c.drawString(0, 4.6 * mm, 'Neocjenjivo: nema potvrđenih ocjena. Nije nula.')
            return
        c.setFillColor(colors.HexColor('#e2e9ee')); c.roundRect(0, 4.2 * mm, self.width, 2.6 * mm, 1.3 * mm, stroke=0, fill=1)
        tone = RED if self.value < 30 else GOLD if self.value < 50 else TEAL
        c.setFillColor(colors.HexColor(tone)); c.roundRect(0, 4.2 * mm, max(2, self.width * min(100, self.value) / 100), 2.6 * mm, 1.3 * mm, stroke=0, fill=1)


class Radar(Flowable):
    """Radar modula. Zatvoren lik se crta samo kad svaki modul ima indeks; inače tačke, jer nepoznato nije nula."""

    def __init__(self, modules, fonts, size=120 * mm):
        super().__init__()
        self.modules, self.fonts, self.width, self.height = modules, fonts, size, size

    def draw(self):
        import math
        c, n, centre, radius = self.canv, len(self.modules), self.width / 2, self.width / 2 - 22 * mm
        point = lambda i, r: (centre + r * math.sin(2 * math.pi * i / n), centre + r * math.cos(2 * math.pi * i / n))
        c.setStrokeColor(colors.HexColor(LINE)); c.setLineWidth(.5)
        for ring in (1 / 3, 2 / 3, 1):
            path = c.beginPath()
            for i in range(n):
                x, y = point(i, radius * ring)
                (path.moveTo if i == 0 else path.lineTo)(x, y)
            path.close(); c.drawPath(path, stroke=1, fill=0)
        for i, module in enumerate(self.modules):
            x, y = point(i, radius); c.line(centre, centre, x, y)
            lx, ly = point(i, radius + 9 * mm)
            c.setFont(self.fonts['bold'], 8); c.setFillColor(colors.HexColor(INK)); c.drawCentredString(lx, ly, module['name'].split(',')[0].split(' i ')[0][:22])
            c.setFont(self.fonts['body'], 7.5); c.setFillColor(colors.HexColor(MUTED)); c.drawCentredString(lx, ly - 3.6 * mm, index_text(module['index']))
        known = [(i, m['index']) for i, m in enumerate(self.modules) if m['index'] is not None]
        c.setStrokeColor(colors.HexColor(TEAL)); c.setFillColor(colors.HexColor(TEAL)); c.setLineWidth(1.4)
        if len(known) == n:
            path = c.beginPath()
            for i, value in known:
                x, y = point(i, radius * value / 100)
                (path.moveTo if i == 0 else path.lineTo)(x, y)
            path.close(); c.setFillColor(colors.Color(.06, .5, .48, alpha=.18)); c.drawPath(path, stroke=1, fill=1)
        else:
            for i, value in known:
                x, y = point(i, radius * value / 100); c.circle(x, y, 1.6 * mm, stroke=0, fill=1)


def _furniture(report, fonts):
    def cover(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(NAVY)); canvas.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor(TEAL)); canvas.rect(0, HEIGHT - 4 * mm, WIDTH, 4 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.white); canvas.setFont(fonts['bold'], 15); canvas.drawString(MARGIN, HEIGHT - 26 * mm, 'MEVAN', charSpace=5)
        canvas.setFont(fonts['bold'], 7.5); canvas.setFillColor(colors.HexColor('#9fb4c4')); canvas.drawString(MARGIN, HEIGHT - 32 * mm, 'EXECUTIVE DIAGNOSTIC', charSpace=1)
        canvas.setFillColor(colors.HexColor(GOLD)); canvas.rect(MARGIN, HEIGHT - 118 * mm, 30 * mm, 1.1 * mm, stroke=0, fill=1)
        title = report['company']
        size = 30 if len(title) <= 22 else 22 if len(title) <= 34 else 16
        canvas.setFillColor(colors.white); canvas.setFont(fonts['display'], size); canvas.drawString(MARGIN, HEIGHT - 134 * mm, title[:60])
        canvas.setFont(fonts['bold'], 10); canvas.drawString(MARGIN, HEIGHT - 145 * mm, 'DIJAGNOSTIKA POSLOVNE ZRELOSTI', charSpace=.6)
        canvas.setFont(fonts['body'], 9.5); canvas.setFillColor(colors.HexColor('#c9d6e0'))
        canvas.drawString(MARGIN, HEIGHT - 156 * mm, 'Šest modula, 65 kriterija: nalazi, uzročne hipoteze, finansijski efekti i plan.')
        canvas.setFillColor(colors.HexColor('#1c3a55')); canvas.roundRect(MARGIN, HEIGHT - 214 * mm, WIDTH - 2 * MARGIN, 38 * mm, 3 * mm, stroke=0, fill=1)
        coverage = report['findings']['maturity']['coverage']
        for x, label, value in ((MARGIN + 8 * mm, 'INDEKS ZRELOSTI', index_text(report['findings']['maturity']['index']).replace('/', ' / ')),
                                (MARGIN + 92 * mm, 'POTVRĐENI KRITERIJI', f"{coverage['confirmed']} / {coverage['criteria']}")):
            canvas.setFont(fonts['bold'], 7); canvas.setFillColor(colors.HexColor('#9fb4c4')); canvas.drawString(x, HEIGHT - 186 * mm, label, charSpace=.6)
            canvas.setFont(fonts['display'], 22); canvas.setFillColor(colors.white); canvas.drawString(x, HEIGHT - 202 * mm, value)
        canvas.setFont(fonts['bold'], 8); canvas.setFillColor(colors.HexColor(GOLD)); canvas.drawString(MARGIN, 34 * mm, report['status'], charSpace=.4)
        canvas.setFont(fonts['body'], 8); canvas.setFillColor(colors.HexColor('#c9d6e0'))
        canvas.drawString(MARGIN, 27 * mm, ' · '.join(x for x in (report['diagnostic'], report['generated']) if x)[:110])
        canvas.drawString(MARGIN, 20 * mm, 'Svi nalazi i finansijski podaci su nacrt do pregleda i odobrenja konsultanta.')
        canvas.restoreState()

    def later(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(NAVY)); canvas.rect(0, HEIGHT - 3 * mm, WIDTH, 3 * mm, stroke=0, fill=1)
        canvas.setFont(fonts['bold'], 7.5); canvas.setFillColor(colors.HexColor(TEAL)); canvas.drawString(MARGIN, HEIGHT - 13 * mm, 'MEVAN  /  DIAGNOSTIC', charSpace=1.2)
        canvas.setFont(fonts['body'], 7.5); canvas.setFillColor(colors.HexColor(MUTED)); canvas.drawRightString(WIDTH - MARGIN, HEIGHT - 13 * mm, (report['company'][:50] + '  |  ' + report['status'])[:120])
        canvas.setStrokeColor(colors.HexColor(LINE)); canvas.setLineWidth(.4); canvas.line(MARGIN, 15 * mm, WIDTH - MARGIN, 15 * mm)
        canvas.setFillColor(colors.HexColor(RED if report['simulated'] else MUTED)); canvas.drawString(MARGIN, 10.5 * mm, 'MEVAN / POVJERLJIVO / ' + report['status'])
        canvas.setFillColor(colors.HexColor(MUTED)); canvas.drawRightString(WIDTH - MARGIN, 10.5 * mm, f'{doc.page:02d}')
        canvas.restoreState()
    return cover, later


def render(data):
    report = prepare(data)
    fonts = register_pdf_fonts()
    def style(name, role='body', size=10, leading=None, color=INK, **extra):
        return ParagraphStyle(name, fontName=fonts[role], fontSize=size, leading=leading or size * 1.45, textColor=colors.HexColor(color), **extra)
    s = {'kicker': style('pk', 'bold', 7.5, color=TEAL, spaceAfter=4), 'title': style('pt', 'display', 21, 25, NAVY, spaceAfter=3),
         'lead': style('pl', size=9.5, color=MUTED, spaceAfter=12), 'body': style('pb', size=9.5, leading=14, spaceAfter=5),
         'small': style('ps', size=8, leading=11.2, color=MUTED, spaceAfter=3), 'label': style('pla', 'bold', 7, 9, MUTED),
         'big': style('pbig', 'display', 19, 22, NAVY), 'h2': style('ph2', 'bold', 8, 10, TEAL, spaceBefore=12, spaceAfter=4),
         'cell': style('pc', size=8.5, leading=11.5), 'cellbold': style('pcb', 'bold', 8.5, 11.5), 'white': style('pw', 'bold', 11, 15.5, '#ffffff'),
         'whitelabel': style('pwl', 'bold', 7, 9, '#9fd8d4'), 'status': style('pst', 'bold', 7.5, 10, RED, spaceBefore=10)}
    text = lambda value, name='body': Paragraph(escape(str(value)).replace('\n', '<br/>'), s[name])
    page_width = WIDTH - 2 * MARGIN
    counter = iter(range(1, 60))
    def head(section, title, lead=''):
        block = [text(f'{next(counter):02d} / {section}', 'kicker'), text(title, 'title')]
        return block + ([text(lead, 'lead')] if lead else [Spacer(1, 8)])
    def box(rows, background=SOFT, padding=9):
        return Table([[rows]], colWidths=[page_width], style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(background)),
                     ('LEFTPADDING', (0, 0), (-1, -1), padding), ('RIGHTPADDING', (0, 0), (-1, -1), padding), ('TOPPADDING', (0, 0), (-1, -1), padding),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), padding), ('ROUNDEDCORNERS', [5, 5, 5, 5])]))
    def stats(items):
        cells = [[text(label.upper(), 'label'), Spacer(1, 3), text(value, 'big'), Spacer(1, 3), text(note, 'small')] for label, value, note in items]
        width = (page_width - 6 * (len(items) - 1)) / len(items)
        return Table([cells], colWidths=[width] * len(items), hAlign='LEFT', spaceAfter=10,
                     style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(SOFT)), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor(TEAL)), ('LEFTPADDING', (0, 0), (-1, -1), 8),
                                       ('RIGHTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                       ('LINEAFTER', (0, 0), (-2, -1), 6, colors.white)]))

    maturity, confidence, finance = report['findings']['maturity'], report['confidence'], report['finance']
    coverage = maturity['coverage']
    scorable = [m for m in report['modules'] if m['index'] is not None]
    story = [Spacer(1, 1), PageBreak()]

    # ---- pregled na jednoj strani
    story += head('EXECUTIVE OVERVIEW', 'Odluka na jednoj strani', 'Stanje zrelosti, pouzdanost nalaza i finansijski potencijal, svaki sa svojim ograničenjem.')
    potential = finance['hypothetical_potential'][mevan_finance_v2.PNL]
    confirmed_pnl = finance['confirmed'][mevan_finance_v2.PNL]
    story.append(stats([
        ('Zrelost', index_text(maturity['index']), f"{coverage['confirmed']} od {coverage['criteria']} kriterija potvrđeno; nepoznato nije nula"),
        ('Pouzdanost', 'Nepoznato' if confidence['score'] is None else f"{confidence['score']:.1f}/100", 'Razred: ' + BAND[confidence['band']] + '; privremeni pragovi, nije kalibrisano'),
        ('Potvrđeni godišnji efekat', number(confirmed_pnl) + ' KM', f'Hipotetički potencijal: {number(potential)} KM/god; nije potvrđena korist'),
    ]))
    if scorable:
        lowest = min(scorable, key=lambda m: m['index'])
        weak = sum(1 for f in lowest['findings'] if f['kind'] == 'KANDIDAT_SLABOST')
        finding = f"{lowest['name']} ima najniži indeks: {index_text(lowest['index'])}, uz {weak} kandidata za slabost. Niska ocjena otvara pitanje; uzrok je hipoteza dok se ne potvrdi dokazom."
    else:
        finding = 'Nijedan modul još nema potvrđene ocjene, pa se najvažniji nalaz ne može izdvojiti. Prvi korak je prikupljanje dokaza.'
    story.append(box([text('NAJVAŽNIJI NALAZ', 'whitelabel'), Spacer(1, 4), text(finding, 'white')], NAVY, 12))
    story.append(text('ODLUKE ZA VLASNIKA', 'h2'))
    ranking = report['ranking']
    if ranking and ranking['options']:
        for option in [o for o in ranking['options'] if o['rank']][:3]:
            first_step = option['steps_30'][0] if option['steps_30'] else 'Koraci za prvih 30 dana nisu uneseni.'
            story += [box([text(f"{option['rank']:02d}  {option['title']}", 'cellbold'), text(first_step, 'small')], SOFT, 8), Spacer(1, 4)]
        story.append(text(('Konačan rang' if ranking['status'] == 'KONAČAN_RANG' else 'Preliminaran rang') + '. Rang nije odobrenje ulaganja ni potvrda koristi.', 'small'))
    else:
        story.append(text('Projektne opcije nisu unesene, pa nema rangiranih odluka.', 'body'))
    story += [text('STATUS: ' + report['status'] + '. Nalazi i finansijski efekti traže odobrenje konsultanta.', 'status'), PageBreak()]

    # ---- metodologija
    story += head('METODOLOGIJA', 'Šta znači indeks zrelosti?', 'Indeks mjeri razvijenost upravljačkih praksi, ne direktno ostvareni poslovni rezultat.')
    story.append(box([text('METODA OBRAČUNA', 'label'), Spacer(1, 4),
                      text('Indeks = 20 × prosjek ocjena (0–5) kriterija koji su primjenjivi i čiji je dokaz potvrdio konsultant. Nepoznato, neprocijenjeno i neprimjenjivo ne ulazi ni u zbir ni u nazivnik. Indeks modula računa se na isti način.')]))
    story.append(Spacer(1, 10))
    for module in report['modules']:
        story.append(Bar(module['name'], module['index'], f"{index_text(module['index'])}  |  {module['verified']} potvrđeno od {module['criteria']}", page_width, fonts))
    story += [Spacer(1, 6), box([text('Tumačenje: nizak indeks znači slabo formalizovane ili nedovoljno potvrđene prakse. Prije zaključka o uzroku i finansijskom efektu potrebna je provjera dokaza. Metodologija 65/6 je nacrt i čeka stručnu potvrdu.', 'small')], '#eaf4f2'), PageBreak()]

    # ---- radar
    story += head('PORTFOLIO MODULA', 'Mapa organizacijske zrelosti', 'Šest modula prikazano istovremeno, radi prepoznavanja neravnoteže.')
    story.append(Table([[Radar(report['modules'], fonts)]], colWidths=[page_width], style=TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')])))
    if len(scorable) >= 2:
        high, low = max(scorable, key=lambda m: m['index']), min(scorable, key=lambda m: m['index'])
        imbalance = f"{high['name']} {index_text(high['index'])} naspram {low['name']} {index_text(low['index'])}."
    else:
        imbalance = 'Za poređenje modula potrebne su potvrđene ocjene u najmanje dva modula.'
    if len(scorable) < len(report['modules']):
        imbalance += ' Radar nije zatvoren: modul bez potvrđenih ocjena je „Neocjenjivo”, a ne nula.'
    story += [Spacer(1, 6), box([text('KLJUČNA NERAVNOTEŽA', 'whitelabel'), Spacer(1, 4), text(imbalance, 'white')], NAVY, 12), PageBreak()]

    # ---- strane po modulima
    for position, module in enumerate(report['modules'], 1):
        story += head(f'ANALIZA MODULA {position}/{len(report["modules"])}', module['name'], 'Dijagnostički nalaz, ocjene po kriterijima, hipoteze i preporuke.')
        gaps = sum(1 for f in module['findings'] if f['kind'] == 'PRAZNINA_U_DOKAZIMA')
        story.append(stats([('Zrelost modula', index_text(module['index']), f"{module['verified']} potvrđeno od {module['criteria']} kriterija"),
                            ('Praznine u dokazima', str(gaps), 'Kriteriji bez ocjene ili dokaza; put za napredak, ne slabost')]))
        rows = [[text('KRITERIJ', 'label'), text('OCJENA', 'label'), text('NALAZ', 'label'), text('PODATAK', 'label')]]
        for finding in module['findings']:
            score = 'N/P' if finding['kind'] == 'NIJE_PRIMJENJIVO' else 'Nepoznato' if finding['score'] is None else f"{finding['score']}/5"
            rows.append([text(f"{finding['code']}  {finding['name']}", 'cell'), text(score, 'cellbold'), text(KIND[finding['kind']], 'cell'), text(finding['nature'].lower(), 'cell')])
        story.append(Table(rows, colWidths=[page_width - 84 * mm, 22 * mm, 36 * mm, 26 * mm], repeatRows=1,
                           style=TableStyle([('LINEBELOW', (0, 0), (-1, 0), .7, colors.HexColor(NAVY)), ('LINEBELOW', (0, 1), (-1, -1), .3, colors.HexColor(LINE)),
                                             ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                                             ('TOPPADDING', (0, 0), (-1, -1), 3.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)])))
        weak = sorted((f for f in module['findings'] if f['kind'] == 'KANDIDAT_SLABOST'), key=lambda f: (f['score'], f['code']))
        story.append(text('NALAZI I UZROČNE HIPOTEZE', 'h2'))
        if not weak:
            story.append(text('U ovom modulu nema kandidata za slabost s ocjenom i dokazom.', 'body'))
        if len(weak) > 3:
            story.append(text(f'Prikazana su tri kandidata s najnižom ocjenom od ukupno {len(weak)}; svi kriteriji su u tabeli iznad.', 'small'))
        for finding in weak[:3]:
            cause = 'Uzrok potvrđen dokazom: ' + finding['cause']['evidence'] if finding['cause']['status'] == 'POTVRĐEN_UZROK' else 'Uzrok je HIPOTEZA: ' + '; '.join(finding['cause']['not_verified_because']) + '.'
            story.append(KeepTogether([text(f"{finding['code']} · {finding['name']} · {finding['score']}/5 · {finding['nature']}", 'cellbold'),
                                       text('Nalaz konsultanta: ' + (finding['claim'] or 'nije unesen.'), 'body'), text(cause, 'small'),
                                       text('Posljedica (hipoteza): ' + finding['consequence']['text'] + '. Preporuka: ' + finding['recommendation'] + '. Vlasnik: ' + finding['owner_role'] + '.', 'small'), Spacer(1, 5)]))
        story.append(PageBreak())
    story.pop()

    cover, later = _furniture(report, fonts)
    buffer = BytesIO()
    SimpleDocTemplate(buffer, pagesize=A4, leftMargin=MARGIN - 6, rightMargin=MARGIN - 6, topMargin=24 * mm - 6, bottomMargin=22 * mm - 6,
                      title='MEVAN Executive Diagnostic — ' + report['company'], author='MEVAN Diagnostic').build(story, onFirstPage=cover, onLaterPages=later, canvasmaker=Canvas)
    return buffer.getvalue()
