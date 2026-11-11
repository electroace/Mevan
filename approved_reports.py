"""Two report views derived from the same approved diagnostic snapshot."""
from io import BytesIO
from datetime import datetime, timezone
import re
import unicodedata
from xml.sax.saxutils import escape

from docx import Document
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph
from project_reports import FONT
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


def report_sections(db, approval_id, view):
    approval = read_approval(db, approval_id)
    ci, di = approval["company_index"], approval["diagnostic_index"]
    prepare_report_manifest(db, approval_id, ci, di)
    company = approval["workspace"]["companies"][ci]
    diagnostic = company["diagnostics"][di]
    review = validate_review(diagnostic)
    records = sorted(diagnostic["quality_records"], key=lambda row: row["criterion_id"])
    modern=approval['policy_version']==2
    demo=approval['report_mode']=='demo'
    heading = "Direktorski izvještaj" if view == "executive" else "Detaljni stručni izvještaj"
    if demo:heading=DEMO_LABEL+' · '+heading
    sections = [("Title", heading), ("Heading2", company.get("company", {}).get("name") or company.get("id", "")),
                ("BodyText", f'{diagnostic.get("name", "")} · ID {approval["diagnostic_id"]}'),
                ("BodyText", f'{"DEMO snimak" if demo else "Odobrenje"} {approval_id} · Revizija {approval["workspace_revision"]} · {"Pripremio" if demo else "Konsultant"} {approval["reviewer_id"]}'),
                ("Heading1", "Sažetak konsultanta"), ("BodyText", review["summary"]),
                ("Heading1", "Tri prioriteta")]
    sections.extend(("BodyText", f'{i}. {review[f"priority{i}"]}') for i in range(1, 4))
    if modern:
        guided=diagnostic.get('guided',{})
        sections.append(('BodyText',f'Odabrani prioritet: {guided.get("selected_candidate", "Nije odabran")} · Projektni nacrt: {guided.get("project_id", "Nije povezan")}'))
    assessment = {r["criterion_id"]: {"score": r["score"], "proof": "confirmed",
                  "evidence": r.get("evidence_reference", "")} for r in records}
    result = approval['report_model']['result'] if modern else analyze({"assess": assessment, "effects": diagnostic.get("effects", [])})
    if demo:
        sections.insert(1,('BodyText',DEMO_LABEL+' — nije stvarno konsultantsko odobrenje, provjera dokaza ili potvrda finansijskog efekta.'))
    if modern:
        sections.insert(3,('BodyText',f'Vrijeme zaključavanja (UTC): {datetime.fromtimestamp(approval["approved_at"],timezone.utc).isoformat()}'))
    sections.extend([("Heading1", "Zrelost po oblastima"),
                     ("BodyText", (f'Ukupni indeks {result["index"]}/100' if result['index'] is not None else 'Neocjenjivo — nema ocijenjenih primjenjivih kriterija') + f' · {len(records)} kriterija')])
    if modern:
        na=[r for r in records if r['verification_status']=='nije_primjenjivo']
        sections.append(('BodyText',f'Primjenjivo {61-len(na)}/61 · N/P {len(na)}. N/P je isključen iz nazivnika; nepoznato nije ocjena nula.'))
    for code, name in DIMENSIONS.items():
        dim=result['dimensions'][code]
        value=f'{dim["index"]}/100' if dim['index'] is not None else 'Neocjenjivo'
        sections.append(("BodyText", f'{name} · {value}'+(f' · primjenjivo {dim["applicable"]}, N/P {dim["na"]}' if modern else '')))
    if modern:
        sections.append(('Radar','Radar zrelosti — samo primjenjivi ocijenjeni kriteriji'))
        if na:
            sections.append(('Heading1','Nije primjenjivo — obuhvat i razlozi'))
            for row in na:
                sections.append(('BodyText',f'{row["criterion_id"]} · N/P · {row["na_reason"]} · Potvrdio konsultant: {row["na_approved_by"]}'))
    sections.append(("Heading1", "Finansijski potencijal"))
    scenarios = result["finance"]["excluded"]
    if not scenarios:
        sections.append(("BodyText", "Nije evidentiran finansijski scenario."))
    for item in scenarios:
        amount = (f'{item["oneoff"]} KM jednokratno' if item["category"] == "working_capital"
                  else f'{item["annual"]} KM godišnje')
        sections.append(("BodyText", f'{item["name"]} · procjena {amount} · {item["reason"]}'))
    sections.append(("Heading1", "Plan za 90 dana"))
    for i, period in enumerate(PERIODS, 1):
        sections.extend([("Heading2", period), ("BodyText", review[f"month{i}"])])
    if view == "detailed":
        sections.append(("Heading1", "Ocjene i trag provjere dokaza"))
        for r in records:
            code = r["criterion_id"]
            if modern and r['verification_status']=='nije_primjenjivo':
                sections.append(('Heading2',f'{code} · {r.get("criterion_name", "")} · N/P (isključeno iz obračuna)'))
                for source,label in [('interview','Intervju'),('documents','Dokumenti'),('visit','Obilazak')]:
                    note=r.get('collection',{}).get(source,'')
                    if note:sections.append(('BodyText',label+': '+str(note)))
                continue
            sections.extend([("Heading2", f'{code} · {r.get("criterion_name", "")} · {r["score"]}/5'),
                             ("BodyText", str(r["evidence_reference"])),
                             ("BodyText", f'Izvor {r.get("source_id", "simulacija" if demo else "")} · Period {r.get("reference_period_start", "—")} – {r.get("reference_period_end", "—")}'),
                             ("BodyText", f'{"Simulirani procjenjivač" if demo else "Procijenio"} {r.get("assessor_id", "DEMO")} · Trag {r.get("verification_audit_ref", "simulirani podaci")}')])
            if modern:
                for source,label in [('interview','Intervju'),('documents','Dokumenti'),('visit','Obilazak')]:
                    note=r.get('collection',{}).get(source,'')
                    sections.append(('BodyText',label+': '+(str(note) if note else 'Nije prikupljeno')))
            finding = diagnostic.get("assess", {}).get(code, {}).get("finding")
            if finding:
                sections.append(("BodyText", str(finding)))
    sections.append(("BodyText", "SHA-256 zaključanog snimka: " + approval["sha256"]))
    return sections


def radar_png(result):
    """Nepoznata ili prazna oblast se ne pretvara u nulu radi crtanja radara."""
    import math
    from PIL import Image, ImageDraw, ImageFont
    values=[result['dimensions'][code]['index'] for code in DIMENSIONS]
    if any(v is None for v in values):
        return None
    picture=Image.new('RGB',(620,360),'white');draw=ImageDraw.Draw(picture)
    font=ImageFont.truetype(str(FONT),14)
    def points(scale):
        return [(310+135*scale[i]*math.sin(2*math.pi*i/5),175-135*scale[i]*math.cos(2*math.pi*i/5)) for i in range(5)]
    for level in (.25,.5,.75,1):draw.polygon(points([level]*5),outline='#bacbd2')
    draw.polygon(points([v/100 for v in values]),fill='#b3e6df',outline='#07556c',width=3)
    for i,name in enumerate(DIMENSIONS.values()):
        x,y=points([1.18]*5)[i];draw.text((x,y),name+' '+str(values[i]),fill='#193448',font=font,anchor='mm')
    output=BytesIO();picture.save(output,format='PNG');output.seek(0);return output


def render(db, approval_id, view, fmt):
    sections = report_sections(db, approval_id, view)
    approval=read_approval(db,approval_id)
    demo=approval['report_mode']=='demo'
    radar=radar_png(approval['report_model']['result']) if approval['report_model'] else None
    buf = BytesIO()
    if fmt == "docx":
        document = Document()
        document.sections[0].header.paragraphs[0].text = DEMO_LABEL if demo else "MEVAN  /  Dijagnostika"
        if demo:document.sections[0].footer.paragraphs[0].text=DEMO_LABEL+' — nije stvarni provjereni nalaz'
        for style, value in sections:
            if style=='Radar':
                if radar:
                    from docx.shared import Inches
                    radar.seek(0);document.add_picture(radar,width=Inches(5.8))
                else:document.add_paragraph('Radar nije prikazan: najmanje jedna oblast je neocjenjiva.')
                continue
            document.add_paragraph(value, style={"BodyText":"Body Text", "Heading1":"Heading 1", "Heading2":"Heading 2"}.get(style, style))
        document.save(buf)
    else:
        pdfmetrics.registerFont(TTFont("MevanReview", FONT))
        base = getSampleStyleSheet()
        styles = {key: ParagraphStyle("review-" + key, parent=base[key], fontName="MevanReview")
                  for key in ("Title", "Heading1", "Heading2", "BodyText")}
        story=[]
        for key,value in sections:
            if key=='Radar':
                if radar:
                    from reportlab.platypus import Image
                    radar.seek(0);story.append(Image(radar,width=465,height=270))
                else:story.append(Paragraph('Radar nije prikazan: najmanje jedna oblast je neocjenjiva.',styles['BodyText']))
            else:story.append(Paragraph(escape(value).replace("\n", "<br/>"), styles[key]))
        def label_page(canvas,doc):
            if demo:
                canvas.setFont('MevanReview',9);canvas.drawString(36,20,DEMO_LABEL+' — nije stvarni provjereni nalaz')
        SimpleDocTemplate(buf, title=sections[0][1]).build(story,onFirstPage=label_page,onLaterPages=label_page)
    return buf.getvalue()
