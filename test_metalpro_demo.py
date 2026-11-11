"""End-to-end offline demo: diagnostic -> candidates -> draft -> persistence -> validation gate -> financials -> reports -> dashboard."""
import os,re,sys,tempfile,importlib
from pathlib import Path
from fastapi.testclient import TestClient
from metalpro_demo import diagnostic,analysis,candidate_ratings,finance_model,demo_summary
from project_candidates import prepare_candidates

def test_61_criteria_and_finance_separation():
    a=diagnostic(); s=demo_summary()
    assert a['coverage']['confirmed']==61 and a['coverage']['independently_verified']==0
    assert a['index']==36.4
    assert {k:v['index'] for k,v in a['dimensions'].items()}=={'F':38.3,'O':34.7,'P':35.0,'L':42.0,'M':33.3}
    assert len(prepare_candidates(a)['candidates'])>=1
    assert all(x['confirmed_annual_benefit_km']==0 and x['confirmed_one_time_benefit_km']==0 for x in s['financial_scenarios'])
    assert s['confirmed_annual_km']==s['confirmed_one_time_km']==0
    realistic=next(x for x in s['financial_scenarios'] if x['name']=='realni')
    assert realistic['one_time_working_capital_release_km']==160000
    assert realistic['annual_gross_benefit_km']==52167

def test_metalpro_full_offline_workflow():
    with tempfile.TemporaryDirectory() as temp:
        os.environ.update(MEVAN_ADMIN_EMAIL='demo@example.test',MEVAN_ADMIN_PASSWORD='A-new-safe-demo-password-123',MEVAN_SESSION_SECRET='s'*48,MEVAN_SECURE_COOKIE='0',MEVAN_DB=str(Path(temp)/'demo.sqlite3'))
        for module in ('server','project_execution'):
            sys.modules.pop(module,None)
        server=importlib.import_module('server')
        with TestClient(server.app,base_url='http://testserver') as client:
            token=re.search(r'name="csrf_token" value="([^"]+)"',client.get('/login').text).group(1)
            assert client.post('/login',data={'csrf_token':token,'email':'demo@example.test','password':'A-new-safe-demo-password-123'},follow_redirects=False).status_code==303
            h={'Origin':'http://testserver'};a=analysis()
            c=client.post('/api/v4/project-candidates',json={'analysis':a},headers=h)
            assert c.status_code==200 and c.json()['candidates']
            ratings=[r.model_dump() for r in candidate_ratings(a)]
            rank=client.post('/api/v4/rank-projects',json={'analysis':a,'ratings':ratings},headers=h)
            assert rank.status_code==200 and rank.json()['candidates'][0]['score'] is not None
            d=client.post('/api/v4/project-draft',json={'analysis':a,'ratings':ratings,'company_id':'METALPRO-DEMO','diagnostic_id':'METALPRO-61-DEMO'},headers=h)
            assert d.status_code==200,d.text
            draft=d.json();assert draft['charter']['baseline_verified'] is False
            created=client.post('/api/v4/projects',json={k:draft[k] for k in ('company_id','diagnostic_id','title','charter')},headers=h)
            assert created.status_code==201,created.text
            pid=created.json()['id'];root=f'/api/v4/projects/{pid}'
            assert client.post(root+'/approve-implementation',headers=h).status_code==409
            fin=client.put(root+'/financial-model',json=finance_model().model_dump(mode='json'),headers=h)
            assert fin.status_code==200,fin.text
            assert client.post(root+'/approve-validation',headers=h).status_code==200
            assert client.post(root+'/weekly-reviews',json={'week':'2026-W46','note':'Nema odobrene implementacije'},headers=h).status_code==409
            assert client.post(root+'/actual-effects',json={'period':'2026-11','name':'Simulirani efekat','category':'operating_saving','amount_km':100,'evidence_reference':'demo','calculation_note':'Simulacija, bez verifikacije','source_owner':'Demo'},headers=h).status_code==409
            for fmt,signature in [('docx',b'PK'),('pdf',b'%PDF')]:
                report=client.get(root+'/report/'+fmt)
                assert report.status_code==200 and report.content.startswith(signature)
            assert client.get('/api/v4/dashboard').status_code==200
            assert client.get(root+'/actual-effects').json()['summary']['independently_verified_km']==0
            assert client.get(root).json()['status']=='validation'
