"""Zaštita DEMO projekta povezanog s vođenim tokom, samo privremeni QA podaci."""
from test_actual_effect_idempotency import project


def test_demo_project_cannot_be_relabelled_or_implemented(project):
    f,_,_=project
    charter={**f.charter,'report_mode':'demo'}
    r=f.client.post('/api/v4/projects',json={'company_id':'QA','diagnostic_id':'DEMO-guided','title':'DEMO — simulirani podaci · pilot','charter':charter},headers=f.headers)
    assert r.status_code==201,r.text
    base='/api/v4/projects/'+r.json()['id']
    assert f.client.put(base+'/charter',json={**charter,'report_mode':'real'},headers=f.headers).status_code==409
    confirmed={**charter,'baseline_verified':True,'targets_approved':True,'checks_completed':True}
    assert f.client.put(base+'/charter',json=confirmed,headers=f.headers).status_code==200
    assert f.client.post(base+'/approve-implementation',headers=f.headers).status_code==409
    assert f.client.get(base).json()['status']=='draft'
    assert f.client.post(base+'/actual-effects',json={'period':'2026-11','name':'DEMO efekat','category':'operating_saving','amount_km':4000,'evidence_reference':'Ogledni izvor','calculation_note':'Simulirani obračun efekta','source_owner':'QA'},headers=f.headers).status_code==409
    for fmt in ['pdf','docx']:
        report=f.client.get(base+'/report/'+fmt);assert report.status_code==200
        if fmt=='docx':
            import io
            from docx import Document
            word=Document(io.BytesIO(report.content))
            assert 'DEMO — simulirani podaci' in word.sections[0].header.paragraphs[0].text
