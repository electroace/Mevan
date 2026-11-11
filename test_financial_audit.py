"""Finance, actuals and weekly history are append-only and transactional."""
import json
from test_project_execution import TestProjectExecution


def test_financial_and_effect_audit():
    fixture=TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        c=fixture.client; h=fixture.headers
        r=c.post('/api/v4/projects',json={'company_id':'audit-finance','diagnostic_id':'d1','title':'METALPRO finansijska provjera','charter':fixture.charter},headers=h)
        assert r.status_code==201,r.text
        pid=r.json()['id']; base=f'/api/v4/projects/{pid}'
        def model(amount):
            return {'scenarios':[{'name':name,'implementation_cost_km':'1000','annual_running_cost_km':'100','benefits':[{'name':'Izbjegnuti trošak','category':'avoided_cost','amount_km':str(amount),'source':'Simulirani ERP','assumption':'Procjena bez dokaza'}]} for name in ('pesimistični','realni','optimistični')]}
        for amount in (500,500,700):
            r=c.put(base+'/financial-model',json=model(amount),headers=h)
            assert r.status_code==200,r.text
        events=c.get(base+'/audit').json()['events']
        assert [e['action'] for e in events]==['created','financial_model_created','financial_model_updated']
        assert json.loads(events[2]['previous_payload'])['scenarios'][0]['benefits'][0]['amount_km']=='500'
        assert json.loads(events[2]['new_payload'])['scenarios'][0]['benefits'][0]['amount_km']=='700'
        assert c.post(base+'/approve-validation',headers=h).status_code==200
        charter=dict(fixture.charter,baseline_verified=True,targets_approved=True,checks_completed=True)
        assert c.put(base+'/charter',json=charter,headers=h).status_code==200
        assert c.post(base+'/approve-implementation',headers=h).status_code==200
        effect={'period':'2026-11','name':'Smanjenje škarta','category':'operating_saving','amount_km':'120.50','evidence_reference':'Simulirani ERP','calculation_note':'Procjena mjesečne razlike','source_owner':'Kontroling','consultant_confirmed':True}
        r=c.post(base+'/actual-effects',json=effect,headers=h)
        assert r.status_code==201,r.text
        eid=r.json()['id']
        assert c.post(base+'/weekly-reviews',json={'week':'2026-W46','note':'Simulirani pregled'},headers=h).status_code==201
        events=c.get(base+'/audit').json()['events']
        assert events[-2]['action']=='actual_effect_recorded'
        assert json.loads(events[-2]['new_payload'])['effect_id']==eid
        assert events[-1]['action']=='weekly_review_created'
        assert json.loads(events[-1]['new_payload'])['week']=='2026-W46'
        assert c.put(base+'/financial-model',json=model(900),headers=h).status_code==409
        assert c.post(base+'/weekly-reviews',json={'week':'2026-W46'},headers=h).status_code==409
        assert len(c.get(base+'/audit').json()['events'])==len(events)
        c.post('/logout',headers=h,follow_redirects=False)
        assert c.get(base+'/audit').status_code==401
    finally:
        fixture.tearDown()
