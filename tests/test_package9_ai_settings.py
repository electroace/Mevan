"""Deveti paket: administrator sam bira AI servis i unosi API ključ."""
import io
import json
import urllib.error

import pytest

import mevan_ai
import test_project_execution as project_fixture

KEY='sk-test-NIJE-STVARAN-kljuc-0123456789abcd'
FORM={'provider':'anthropic','model':'claude-sonnet-5-5','api_key':KEY}


@pytest.fixture
def fx(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


class Reply:
    def __init__(self,payload):self.payload=payload
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def read(self,limit=None):return json.dumps(self.payload).encode()


def capture(monkeypatch,payload):
    seen=[]
    def fake(request,timeout=None):
        seen.append(request);return Reply(payload)
    monkeypatch.setattr(mevan_ai.urllib.request,'urlopen',fake)
    return seen


def test_key_is_saved_encrypted_and_never_returned(fx):
    r=fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    assert r.status_code==200,r.text
    body=r.json()
    assert body['source']=='app' and body['provider']=='anthropic' and body['key_set'] is True and body['key_hint']==KEY[-4:]
    for text in (r.text,fx.client.get('/api/ai/settings').text,fx.client.get('/api/backup').text,fx.client.get('/api/audit').text):
        assert KEY not in text
    assert KEY.encode() not in open(fx.server.DB,'rb').read()
    assert mevan_ai.active_config(fx.server.DB)=={'provider':'anthropic','model':'claude-sonnet-5-5','base_url':'https://api.anthropic.com/v1','key':KEY}


def test_settings_need_login_and_same_origin(fx):
    assert fx.client.put('/api/ai/settings',json=FORM,headers={'Origin':'https://evil.example'}).status_code==403
    assert fx.client.delete('/api/ai/settings',headers={'Origin':'https://evil.example'}).status_code==403
    assert fx.client.post('/api/ai/test',headers={'Origin':'https://evil.example'}).status_code==403
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.get('/api/ai/settings').status_code==401
    assert fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers).status_code==401


def test_blank_key_keeps_existing_only_for_same_service(fx):
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    r=fx.client.put('/api/ai/settings',json={'provider':'anthropic','model':'claude-haiku-5-5','api_key':''},headers=fx.headers)
    assert r.status_code==200 and r.json()['model']=='claude-haiku-5-5' and r.json()['key_hint']==KEY[-4:]
    r=fx.client.put('/api/ai/settings',json={'provider':'openai','model':'gpt-4.1-mini','api_key':''},headers=fx.headers)
    assert r.status_code==422 and 'Unesite API ključ' in r.json()['detail']
    assert mevan_ai.active_config(fx.server.DB)['provider']=='anthropic'


@pytest.mark.parametrize('form',[
    {'provider':'nepoznat','model':'m','api_key':KEY},
    {'provider':'openai','model':'ima razmak','api_key':KEY},
    {'provider':'openai','model':'gpt-4.1-mini','api_key':'kratak'},
    {'provider':'compatible','model':'m','api_key':KEY,'base_url':'http://example.com/v1'},
    {'provider':'compatible','model':'m','api_key':KEY,'base_url':'https://localhost/v1'},
    {'provider':'compatible','model':'m','api_key':KEY,'base_url':'https://10.0.0.5/v1'},
    {'provider':'compatible','model':'m','api_key':KEY,'base_url':'https://user:pass@example.com/v1'},
])
def test_invalid_settings_are_rejected_without_echoing_the_key(fx,form):
    r=fx.client.put('/api/ai/settings',json=form,headers=fx.headers)
    assert r.status_code==422 and KEY not in r.text
    assert fx.client.get('/api/ai/settings').json()['source']=='none'


def test_environment_key_still_works_and_entered_key_wins(fx,monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','env-kljuc-nije-stvaran-0123456789')
    assert fx.client.get('/api/ai/settings').json()['source']=='environment'
    assert mevan_ai.active_config(fx.server.DB)['provider']=='openai'
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    assert mevan_ai.active_config(fx.server.DB)['key']==KEY
    assert fx.client.delete('/api/ai/settings',headers=fx.headers).json()['source']=='environment'


def test_changed_server_secret_makes_stored_key_unusable_not_wrong(fx,monkeypatch):
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    monkeypatch.setenv('MEVAN_SESSION_SECRET','druga-tajna-0123456789-0123456789-0123456789')
    assert mevan_ai.active_config(fx.server.DB) is None


def test_openai_and_compatible_requests(monkeypatch):
    body={'model':'zanemaren','messages':[{'role':'system','content':'S'},{'role':'user','content':'U'}],'temperature':0.1,'max_tokens':50}
    seen=capture(monkeypatch,{'choices':[{'message':{'content':'odgovor'}}]})
    assert mevan_ai.chat({'provider':'openai','model':'gpt-x','base_url':'https://api.openai.com/v1','key':KEY},body)=='odgovor'
    assert mevan_ai.chat({'provider':'compatible','model':'m','base_url':'https://ai.example.com/v1','key':KEY},body)=='odgovor'
    assert [r.full_url for r in seen]==['https://api.openai.com/v1/chat/completions','https://ai.example.com/v1/chat/completions']
    sent=json.loads(seen[0].data)
    assert sent['model']=='gpt-x' and sent['messages']==body['messages'] and seen[0].get_header('Authorization')=='Bearer '+KEY


def test_claude_request_is_translated_and_json_fences_are_removed(monkeypatch):
    body={'model':'zanemaren','messages':[{'role':'system','content':'Sistem'},{'role':'user','content':'Pitanje'}],
          'response_format':{'type':'json_object'},'temperature':0.1,'max_tokens':77}
    seen=capture(monkeypatch,{'content':[{'type':'text','text':'```json\n{"a": 1}\n```'}]})
    text=mevan_ai.chat({'provider':'anthropic','model':'claude-sonnet-5-5','base_url':'https://api.anthropic.com/v1','key':KEY},body)
    assert json.loads(text)=={'a':1}
    request=seen[0];sent=json.loads(request.data)
    assert request.full_url=='https://api.anthropic.com/v1/messages'
    assert request.get_header('X-api-key')==KEY and request.get_header('Anthropic-version')=='2023-06-01' and request.get_header('Authorization') is None
    assert sent['model']=='claude-sonnet-5-5' and sent['max_tokens']==77 and sent['messages']==[{'role':'user','content':'Pitanje'}]
    assert sent['system'].startswith('Sistem') and 'JSON' in sent['system'] and 'response_format' not in sent


def test_connection_check_reports_http_code_without_details(fx,monkeypatch):
    assert fx.client.post('/api/ai/test',headers=fx.headers).status_code==503
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    def refused(request,timeout=None):
        raise urllib.error.HTTPError(request.full_url,401,'Unauthorized',{},io.BytesIO(b'{"error":"bad key '+KEY.encode()+b'"}'))
    monkeypatch.setattr(mevan_ai.urllib.request,'urlopen',refused)
    r=fx.client.post('/api/ai/test',headers=fx.headers)
    assert r.status_code==502 and 'HTTP 401' in r.json()['detail'] and KEY not in r.text
    capture(monkeypatch,{'content':[{'type':'text','text':'OK'}]})
    assert fx.client.post('/api/ai/test',headers=fx.headers).json()=={'ok':True,'provider':'anthropic','model':'claude-sonnet-5-5'}


def test_ai_draft_uses_the_entered_service(fx,monkeypatch):
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    seen=capture(monkeypatch,{'content':[{'type':'text','text':'Nacrt iz Claude servisa'}]})
    r=fx.client.post('/api/ai/draft',json={'dimension':'F','criteria':[{'code':'F01','name':'Profitabilnost','score':'2','proof':'confirmed','finding':'Nalaz','evidence':'Dokaz','kpi':'','recommendation':'','applicable':'yes','financial':''}],'financial_effects':[]},headers=fx.headers)
    assert r.status_code==200,r.text
    assert r.json()['draft']=='Nacrt iz Claude servisa' and seen[0].full_url.endswith('/v1/messages')
