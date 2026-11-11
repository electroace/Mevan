"""Retry safety on disposable SQLite databases, including concurrent requests."""
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def project(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('MEVAN_CANDIDATE_DATABASE_URL', raising=False)
    from test_project_execution import TestProjectExecution
    f = TestProjectExecution(methodName='test_auth_origin_and_gate')
    f.setUp()
    try:
        def create(diagnostic):
            result = f.client.post('/api/v4/projects', json=dict(company_id='QA', diagnostic_id=diagnostic,
                                   title='Izolovani projekat provjere', charter=f.charter), headers=f.headers)
            assert result.status_code == 201, result.text
            pid = result.json()['id']
            charter = dict(f.charter, baseline_verified=True, targets_approved=True, checks_completed=True)
            assert f.client.put(f'/api/v4/projects/{pid}/charter', json=charter, headers=f.headers).status_code == 200
            assert f.client.post(f'/api/v4/projects/{pid}/approve-implementation', headers=f.headers).status_code == 200
            return f'/api/v4/projects/{pid}/actual-effects'
        yield f, create('prva'), create
    finally:
        f.tearDown()


def effect(**changes):
    return dict(dict(period='2026-11', name='Smanjenje škarta', category='operating_saving', amount_km='4000',
                     evidence_reference='QA-račun-1', calculation_note='Razlika troškova škarta za isti period',
                     source_owner='Kontroling', consultant_confirmed=True), **changes)


def post(f, url, payload=None, key=None):
    return f.client.post(url, json=payload or effect(), headers={**f.headers, **({'Idempotency-Key': key} if key is not None else {})})


def test_4000_twice_is_one_effect_and_one_audit(project):
    f, url, _ = project
    a, b = post(f, url), post(f, url, effect(amount_km='4000.00'))
    assert a.status_code == b.status_code == 201
    assert a.json()['id'] == b.json()['id']
    assert not a.json()['replayed'] and b.json()['replayed']
    data = f.client.get(url).json()
    assert len(data['entries']) == 1
    assert data['summary']['consultant_confirmed_recurring_km'] == 4000
    events = f.client.get(url.replace('/actual-effects', '/audit')).json()['events']
    assert sum(e['action'] == 'actual_effect_recorded' for e in events) == 1


@pytest.mark.parametrize('key', [None, 'racun-1'])
def test_simultaneous_retries_create_exactly_one_row(project, key):
    f, url, _ = project
    barrier = Barrier(6)
    def submit(_):
        with TestClient(f.server.app, base_url='http://testserver', cookies=f.client.cookies) as client:
            barrier.wait(timeout=10)
            return client.post(url, json=effect(), headers={**f.headers, **({'Idempotency-Key':key} if key else {})})
    with ThreadPoolExecutor(max_workers=6) as pool:
        responses = list(pool.map(submit, range(6)))
    assert [r.status_code for r in responses] == [201]*6
    assert len({r.json()['id'] for r in responses}) == 1
    assert sum(not r.json()['replayed'] for r in responses) == 1
    assert f.client.get(url).json()['summary']['consultant_confirmed_recurring_km'] == 4000
    events = f.client.get(url.replace('/actual-effects', '/audit')).json()['events']
    assert sum(e['action'] == 'actual_effect_recorded' for e in events) == 1


def test_distinct_events_and_changed_evidence_are_preserved(project):
    f, url, _ = project
    responses = [post(f,url,key='dogadjaj-1'), post(f,url,key='dogadjaj-2'),
                 post(f,url,effect(evidence_reference='QA-račun-2')), post(f,url,effect(period='2026-12'))]
    assert all(r.status_code == 201 for r in responses)
    assert len({r.json()['id'] for r in responses}) == 4
    assert len(f.client.get(url).json()['entries']) == 4


def test_key_cannot_be_reused_for_changed_content(project):
    f, url, _ = project
    assert post(f,url,key='isti-dogadjaj').status_code == 201
    assert post(f,url,effect(amount_km=5000),key='isti-dogadjaj').status_code == 409
    assert f.client.get(url).json()['summary']['consultant_confirmed_recurring_km'] == 4000


def test_key_is_scoped_to_project(project):
    f, url, create = project
    other = create('druga')
    a, b = post(f,url,key='racun-1'), post(f,other,key='racun-1')
    assert a.status_code == b.status_code == 201 and a.json()['id'] != b.json()['id']


def test_existing_legacy_rows_are_not_modified_or_merged(project):
    f, url, _ = project
    pid = url.split('/')[-2]
    legacy = [(f'legacy-{i}',pid,json.dumps(effect()),123) for i in (1,2)]
    with sqlite3.connect(f.server.DB) as db:
        db.executemany('INSERT INTO v4_actual_effects VALUES(?,?,?,?)',legacy)
    post(f,url);post(f,url)
    with sqlite3.connect(f.server.DB) as db:
        assert db.execute("SELECT * FROM v4_actual_effects WHERE id LIKE 'legacy-%' ORDER BY id").fetchall() == legacy
    assert len(f.client.get(url).json()['entries']) == 3


def test_failed_audit_rolls_back_effect_and_allows_retry(project, monkeypatch):
    f, url, _ = project
    import project_execution
    original = project_execution.record_audit
    def fail(*args):
        raise RuntimeError('Namjerni kvar za provjeru transakcije')
    monkeypatch.setattr(project_execution,'record_audit',fail)
    with pytest.raises(RuntimeError):
        post(f,url,key='retry-poslije-kvara')
    assert f.client.get(url).json()['entries'] == []
    monkeypatch.setattr(project_execution,'record_audit',original)
    assert post(f,url,key='retry-poslije-kvara').status_code == 201


def test_invalid_payload_and_key_are_rejected_without_writes(project):
    f, url, _ = project
    assert post(f,url,effect(amount_km=-1)).status_code == 422
    assert post(f,url,key='nedozvoljena oznaka').status_code == 422
    assert f.client.get(url).json()['entries'] == []
