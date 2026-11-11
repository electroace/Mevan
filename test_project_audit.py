"""Audit history must retain before/after values and reject unauthorized access."""
from test_project_execution import TestProjectExecution


def test_project_audit_history():
    fixture=TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        client=fixture.client
        payload={'company_id':'audit-demo','diagnostic_id':'audit-diagnostic','title':'Provjera historije promjena','charter':fixture.charter}
        response=client.post('/api/v4/projects',json=payload,headers=fixture.headers)
        assert response.status_code==201,response.text
        pid=response.json()['id']
        url=f'/api/v4/projects/{pid}/audit'
        assert [x['action'] for x in client.get(url).json()['events']]==['created']
        assert client.put(f'/api/v4/projects/{pid}/charter',json=fixture.charter,headers=fixture.headers).status_code==200
        assert len(client.get(url).json()['events'])==1  # no-op does not create an event
        edited=dict(fixture.charter,objective='Provjeriti dokumentovane dokaze i uzroke')
        assert client.put(f'/api/v4/projects/{pid}/charter',json=edited,headers=fixture.headers).status_code==200
        assert client.post(f'/api/v4/projects/{pid}/approve-validation',headers=fixture.headers).status_code==200
        events=client.get(url).json()['events']
        assert [x['action'] for x in events]==['created','charter_edited','validation_approved']
        import json
        assert json.loads(events[1]['previous_payload'])['objective']==fixture.charter['objective']
        assert json.loads(events[1]['new_payload'])['objective']==edited['objective']
        assert client.get('/api/v4/projects/not-a-project/audit').status_code==404
        client.post('/logout',headers=fixture.headers,follow_redirects=False)
        assert client.get(url).status_code==401
    finally:
        fixture.tearDown()
