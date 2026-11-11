"""Sintetičke regresije drugog paketa, bez udaljenih servisa ili stvarnih podataka."""
import copy
import hashlib
import io
import json
import sqlite3
import subprocess

import pytest
from docx import Document
from fastapi import FastAPI
from fastapi.testclient import TestClient

from diagnostic_engine import DIMENSIONS, analyze
from mevan_report_gate import evaluate_report_gate
from mevan_report_model import DEMO_LABEL
from mevan_test_approval import read_approval
from mevan_test_report_manifest import prepare_report_manifest
from mevan_test_workspace_api import create_test_router
from test_approved_delivery import diagnostic


def na(row):
    row.update(verification_status='nije_primjenjivo',score=None,na_reason='Kompanija ne koristi ovaj proces u dokumentovanom obuhvatu dijagnostike.',na_approved_by='QA-konsultant',is_simulated=False)


@pytest.fixture
def api(tmp_path):
    path=tmp_path/'package2.db';app=FastAPI()
    app.include_router(create_test_router(str(path),lambda r:True,lambda r:True,'QA-konsultant'))
    with TestClient(app) as client:yield client,path,tmp_path


def save(client,d,rev=0):
    return client.put('/api/test/v2/workspace',json={'workspace':{'companies':[{'id':'QA','company':{'name':'QA proizvodnja'},'diagnostics':[d]}]},'expected_revision':rev})


def approve(client,rev=1):
    return client.post('/api/test/v2/approvals',json={'expected_revision':rev,'company_index':0,'diagnostic_index':0})


def doc_text(client,aid,view,fmt,tmp_path,query=''):
    r=client.get(f'/api/test/v2/approvals/{aid}/{view}/{fmt}'+query);assert r.status_code==200,r.text
    if fmt=='docx':
        d=Document(io.BytesIO(r.content))
        return '\n'.join(p.text for p in d.paragraphs),r,d
    path=tmp_path/f'{view}.pdf';path.write_bytes(r.content)
    return subprocess.check_output(['pdftotext',str(path),'-']).decode(),r,None


@pytest.mark.parametrize('excluded',['F','O','P','L','M','mixed','all'])
def test_na_indices_and_empty_dimensions(api,excluded):
    client,path,tmp=api;d=diagnostic('NP')
    for i,row in enumerate(d['quality_records']):
        row['score']=i%6
        if excluded=='all' or row['criterion_id'].startswith(excluded) or (excluded=='mixed' and i%3==0):na(row)
    assert save(client,d).status_code==200
    approval=approve(client);assert approval.status_code==200,approval.text;aid=approval.json()['approval_id']
    with sqlite3.connect(path) as db:
        model=read_approval(db,aid)['report_model']['result']
        for code in [None,*DIMENSIONS]:
            rows=[r for r in d['quality_records'] if (code is None or r['criterion_id'].startswith(code)) and r['verification_status']!='nije_primjenjivo']
            expected=round(sum(r['score'] for r in rows)/len(rows)*20,1) if rows else None
            assert (model if code is None else model['dimensions'][code])['index']==expected
        assert model['coverage']['applicable']==sum(r['verification_status']!='nije_primjenjivo' for r in d['quality_records'])
    for view in ['executive','detailed']:
        for fmt in ['pdf','docx']:
            text,_,_=doc_text(client,aid,view,fmt,tmp)
            assert 'N/P' in text and 'QA-konsultant' in text and 'Kompanija ne koristi' in text
            if excluded=='all':assert 'Neocjenjivo' in text and '0/100' not in text


@pytest.mark.parametrize('change',[{'na_reason':''},{'na_reason':'x'},{'na_reason':'test '*8},{'na_approved_by':''},{'score':0}])
def test_undocumented_na_blocks(api,change):
    client,_,_=api;d=diagnostic('NP');na(d['quality_records'][0]);d['quality_records'][0].update(change)
    assert save(client,d).status_code==200
    assert approve(client).status_code==422
    assert client.get('/api/test/v2/approvals').json()==[]


@pytest.mark.parametrize('status',['nema_podataka','samoprocjena','dokumentovano_neprovjereno','simulacija'])
def test_applicable_unverified_still_blocks_real(api,status):
    client,_,_=api;d=diagnostic('real');d['quality_records'][0]['verification_status']=status
    if status=='nema_podataka':d['quality_records'][0]['score']=None
    assert save(client,d).status_code==200
    assert approve(client).status_code==422


def demo_diagnostic():
    d=diagnostic('METALPRO-synthetic');d['report_mode']='demo'
    for row in d['quality_records']:
        row.update(verification_status='simulacija',is_simulated=True,evidence_reference='SIMULACIJA — ogledna evidencija '+row['criterion_id'],collection=dict(interview='Simulirani intervju',documents='Ogledni dokument',visit='Simulirani obilazak'))
    return d


def test_demo_mode_locked_manifest_labels_and_four_formats(api):
    client,path,tmp=api;d=demo_diagnostic();na(d['quality_records'][0])
    assert save(client,d).status_code==200
    approval=approve(client);assert approval.status_code==200,approval.text;aid=approval.json()['approval_id']
    with sqlite3.connect(path) as db:
        a=read_approval(db,aid);manifest=prepare_report_manifest(db,aid,0,0)
        assert a['report_mode']==manifest['report_mode']=='demo'
        assert a['policy_version']==manifest['policy_version']==2
    for view in ['executive','detailed']:
        for fmt in ['pdf','docx']:
            text,r,word=doc_text(client,aid,view,fmt,tmp,'?mode=real&report_mode=real')
            assert DEMO_LABEL in text and 'nije stvarno' in text
            assert 'Odobrenje ' not in text and '_DEMO_' in r.headers['content-disposition']
            if word:
                assert DEMO_LABEL in word.sections[0].header.paragraphs[0].text
                assert DEMO_LABEL in word.sections[0].footer.paragraphs[0].text
            else:
                pages=[p for p in text.split('\f') if p.strip()]
                assert all(DEMO_LABEL in p for p in pages)
    d['report_mode']='real';assert save(client,d,1).status_code==200
    assert approve(client,2).status_code==422
    assert client.get('/api/test/v2/approvals').json()[0]['report_mode']=='demo'
    assert DEMO_LABEL in doc_text(client,aid,'executive','docx',tmp)[0]


@pytest.mark.parametrize('change',['mixed_verified','missing_evidence','claim','missing_score'])
def test_demo_cannot_certify_verified_claims_or_skip_data(api,change):
    client,_,_=api;d=demo_diagnostic()
    if change=='mixed_verified':d['quality_records'][0].update(verification_status='provjereno',is_simulated=False)
    if change=='missing_evidence':d['quality_records'][0]['evidence_reference']=''
    if change=='missing_score':d['quality_records'][0]['score']=None
    if change=='claim':d['finance_claims']=[{'validation_status':'independently_verified','baseline_reference':'x','calculation_reference':'y'}]
    assert save(client,d).status_code==200
    assert approve(client).status_code==422


def test_explicit_real_mode_cannot_relabel_simulated_source(api):
    client,_,_=api;d=diagnostic('real');d['assess']={'F01':{'evidence':'SIMULACIJA — pretpostavljeni nalaz'}}
    assert save(client,d).status_code==200
    assert approve(client).status_code==422


def test_frozen_model_and_collection_survive_later_work_and_restore(api,monkeypatch):
    client,path,tmp=api;d=diagnostic('guided')
    d['quality_records'][0]['collection']={'interview':'Razgovor s planerom 10.11.2026.','documents':'ERP izvještaj Q3, oznaka 23.','visit':'Obilazak linije A, zapis 11.'}
    d['guided']={'current_stage':'plan','selected_candidate':'C3','project_id':'project-qa','owner':'Planer'}
    assert save(client,d).status_code==200
    approval=approve(client);assert approval.status_code==200;aid=approval.json()['approval_id']
    before=doc_text(client,aid,'detailed','docx',tmp)[0]
    loaded=client.get('/api/test/v2/workspace').json()['workspace']['companies'][0]['diagnostics'][0]
    assert loaded['guided']==d['guided'] and loaded['quality_records'][0]['collection']==d['quality_records'][0]['collection']
    d['consultant_review']['summary']='Kasnija izmjena';d['quality_records'][0]['score']=0
    assert save(client,d,1).status_code==200
    monkeypatch.setattr('approved_reports.analyze',lambda *a,**kw:(_ for _ in ()).throw(AssertionError('Ne smije ponovo računati zaključani model')))
    assert doc_text(client,aid,'detailed','docx',tmp)[0]==before
    from backup_restore import backup,restore
    backup(path,tmp/'backup.db');restore(tmp/'backup.db',tmp/'restore.db')
    with sqlite3.connect(tmp/'restore.db') as db:
        assert read_approval(db,aid)['sha256']==approval.json()['sha256']


def test_historical_v1_snapshot_keeps_old_reader(api):
    client,path,tmp=api;d=diagnostic('historical')
    assert save(client,d).status_code==200
    aid=approve(client).json()['approval_id']
    with sqlite3.connect(path) as db:
        raw=json.loads(db.execute('SELECT snapshot_json FROM diagnostic_approvals_test WHERE approval_id=?',(aid,)).fetchone()[0])
        raw['format']='mevan-bound-approval-v1';raw.pop('report_model');raw.pop('report_mode')
        raw['workspace']['companies'][0]['diagnostics'][0]['consultant_review']={key:'x' for key in d['consultant_review']}
        encoded=json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':'))
        db.execute('UPDATE diagnostic_approvals_test SET snapshot_json=?,sha256=? WHERE approval_id=?',(encoded,hashlib.sha256(encoded.encode()).hexdigest(),aid))
    for view in ['executive','detailed']:
        for fmt in ['docx','pdf']:assert 'historical' in doc_text(client,aid,view,fmt,tmp)[0]


def test_working_engine_empty_applicable_is_none():
    result=analyze({'assess':{r['criterion_id']:{'applicable':'no'} for r in diagnostic('x')['quality_records']}})
    assert result['index'] is None and result['coverage']['applicable']==0
    assert all(d['index'] is None for d in result['dimensions'].values())


def test_minimal_justified_na_does_not_require_applicable_evidence_fields(api):
    client,_,tmp=api;d=diagnostic('minimal-na')
    d['quality_records'][0]={'criterion_id':'F01','verification_status':'nije_primjenjivo','score':None,
        'na_reason':'Ovaj proces nije prisutan u dokumentovanom obuhvatu procjene.','na_approved_by':'QA-konsultant'}
    assert save(client,d).status_code==200
    r=approve(client);assert r.status_code==200,r.text
    for view in ['executive','detailed']:
        for fmt in ['docx','pdf']:assert 'N/P' in doc_text(client,r.json()['approval_id'],view,fmt,tmp)[0]


@pytest.mark.parametrize('value',[None,[],{'interview':42},{'documents':['nedozvoljen oblik']}])
def test_malformed_collection_is_rejected_without_losing_workspace(api,value):
    client,_,_=api;d=diagnostic('guided');assert save(client,d).status_code==200
    before=client.get('/api/test/v2/workspace').json()
    d['quality_records'][0]['collection']=value
    assert save(client,d,1).status_code==422
    assert client.get('/api/test/v2/workspace').json()==before


def test_inconsistent_snapshot_mode_fails_closed(api):
    client,path,_=api;d=demo_diagnostic();assert save(client,d).status_code==200
    aid=approve(client).json()['approval_id']
    with sqlite3.connect(path) as db:
        raw=json.loads(db.execute('SELECT snapshot_json FROM diagnostic_approvals_test WHERE approval_id=?',(aid,)).fetchone()[0])
        raw['report_mode']='real'
        encoded=json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':'))
        db.execute('UPDATE diagnostic_approvals_test SET snapshot_json=?,sha256=? WHERE approval_id=?',(encoded,hashlib.sha256(encoded.encode()).hexdigest(),aid))
    assert client.get(f'/api/test/v2/approvals/{aid}/executive/pdf').status_code==422
