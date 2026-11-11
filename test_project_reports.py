from io import BytesIO
from docx import Document
from project_reports import build_sections,export_docx,export_pdf

def sample():
 return dict(title='METALPRO DEMO — validacija',company_id='METALPRO-DEMO',diagnostic_id='demo',status='draft',approved_at=None,charter=dict(problem='Neprovjerene pretpostavke o zastoju',objective='Provjeriti početno stanje i uzroke',scope='Pilot',methodology='DMAIC',activities=[],kpis=[],assumptions=[],required_checks=[],baseline_verified=False,targets_approved=False,checks_completed=False),finance=None,reviews=[],effects=[])

def test_reports_are_real_documents():
 data=sample();word=export_docx(data);pdf=export_pdf(data)
 assert word[:2]==b'PK' and pdf[:4]==b'%PDF'
 text='\n'.join(p.text for p in Document(BytesIO(word)).paragraphs)
 assert 'METALPRO DEMO' in text and 'Nezavisno verificirano' in text and '0 KM' in text

def test_no_estimated_values_are_confirmed():
 sections=build_sections(sample());all_text=' '.join(v for _,items in sections for _,v in items)
 assert '0 KM' in all_text and 'Finansijski model nije unesen' in all_text
