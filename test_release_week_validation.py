"""Regression: reject impossible ISO week labels before storing reviews."""
from pydantic import ValidationError
from project_execution import ReviewIn
from test_project_execution import TestProjectExecution


def test_iso_week_validation():
    for week in ('2026-W00','2026-W54','2025-W53','2027-W53'):
        try:
            ReviewIn(week=week)
        except ValidationError:
            pass
        else:
            raise AssertionError(f'Invalid week accepted: {week}')
    assert ReviewIn(week='2020-W53').week == '2020-W53'
    assert ReviewIn(week='2026-W46').week == '2026-W46'


def test_invalid_week_does_not_create_review_or_audit():
    fixture=TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        c,h=fixture.client,fixture.headers
        r=c.post('/api/v4/projects',json={'company_id':'iso','diagnostic_id':'d1','title':'Provjera ISO sedmice','charter':fixture.charter},headers=h)
        assert r.status_code==201,r.text
        pid=r.json()['id']; base=f'/api/v4/projects/{pid}'
        assert c.post(base+'/approve-validation',headers=h).status_code==200
        charter=dict(fixture.charter,baseline_verified=True,targets_approved=True,checks_completed=True)
        assert c.put(base+'/charter',json=charter,headers=h).status_code==200
        assert c.post(base+'/approve-implementation',headers=h).status_code==200
        audit_before=len(c.get(base+'/audit').json()['events'])
        for week in ('2026-W00','2025-W53','2026-W99'):
            response=c.post(base+'/weekly-reviews',json={'week':week},headers=h)
            assert response.status_code==422,(week,response.text)
        assert c.get(base).json()['weekly_reviews']==[]
        assert len(c.get(base+'/audit').json()['events'])==audit_before
        assert c.post(base+'/weekly-reviews',json={'week':'2026-W46'},headers=h).status_code==201
    finally:
        fixture.tearDown()
