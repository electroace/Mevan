import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from approved_reports import REVIEW_FIELDS, validate_review
from mevan_test_approval import ApprovalError, approve_workspace, init_approval_store
from mevan_test_workspace_api import create_test_router
from test_approved_delivery import diagnostic


@pytest.fixture
def review_api(tmp_path):
    path=tmp_path/'review.db'
    app=FastAPI()
    app.include_router(create_test_router(str(path),lambda r:True,lambda r:True,'QA-konsultant'))
    with TestClient(app) as client:
        yield client,path


def save_and_approve(client, d):
    assert client.put('/api/test/v2/workspace',json={'expected_revision':0,'workspace':{'companies':[{'id':'QA','diagnostics':[d]}]}}).status_code == 200
    return client.post('/api/test/v2/approvals',json={'expected_revision':1,'company_index':0,'diagnostic_index':0})


@pytest.mark.parametrize('value',['','   ','x','TODO','test '*40,'Lorem ipsum dolor sit amet '*8,'1234 '*40,'sadržaj '*40])
def test_placeholder_in_all_seven_fields_cannot_be_approved(review_api,value):
    client,path=review_api
    d=diagnostic('QA');d['consultant_review']={key:value for key in REVIEW_FIELDS}
    response=save_and_approve(client,d)
    assert response.status_code == 422
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM diagnostic_approvals_test').fetchone()[0] == 0


@pytest.mark.parametrize('field',list(REVIEW_FIELDS))
def test_each_field_is_independently_required(field):
    d=diagnostic('QA');d['consultant_review'][field]='x'
    with pytest.raises(ApprovalError):
        validate_review(d,for_approval=True)


def test_valid_bosnian_review_approves_and_downloads_four_formats(review_api):
    client,_=review_api
    r=save_and_approve(client,diagnostic('QA'));assert r.status_code == 200,r.text
    for view in ('executive','detailed'):
        for fmt in ('docx','pdf'):
            doc=client.get(f'/api/test/v2/approvals/{r.json()["approval_id"]}/{view}/{fmt}')
            assert doc.status_code == 200


def test_historical_short_approved_content_remains_readable(review_api):
    client,path=review_api
    d=diagnostic('historijska');d['consultant_review']={k:'x' for k in REVIEW_FIELDS}
    # Reconstruct an already-approved bound snapshot under the old policy.
    assert save_and_approve(client,d).status_code == 422
    with sqlite3.connect(path,isolation_level=None) as db:
        init_approval_store(db)
        approval=approve_workspace(db,1,'raniji-konsultant',0,0)
    for view in ('executive','detailed'):
        for fmt in ('pdf','docx'):
            assert client.get(f'/api/test/v2/approvals/{approval["approval_id"]}/{view}/{fmt}').status_code == 200


def test_malformed_review_is_a_validation_error():
    for value in (None,[], 'tekst'):
        with pytest.raises(ApprovalError):
            validate_review({'consultant_review':value},for_approval=True)
