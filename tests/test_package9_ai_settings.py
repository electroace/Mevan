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
    active=mevan_ai.active_config(fx.server.DB)
    assert {k:active[k] for k in ('provider','model','base_url','key')}=={'provider':'anthropic','model':'claude-sonnet-5-5','base_url':'https://api.anthropic.com/v1','key':KEY}


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
    assert sent['model']=='claude-sonnet-5-5' and sent['messages']==[{'role':'user','content':'Pitanje'}]
    # Noviji Claude modeli odbijaju temperature (HTTP 400) i razmišljaju prije odgovora, pa max_tokens ima rezervu.
    assert 'temperature' not in sent and 'top_p' not in sent and sent['max_tokens']==77*2+mevan_ai.ANTHROPIC_THINKING_HEADROOM
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


def test_claude_reply_with_thinking_block_before_text_is_read(monkeypatch):
    capture(monkeypatch,{'content':[{'type':'thinking','thinking':'razmišljanje'},{'type':'text','text':'Odgovor'}]})
    config={'provider':'anthropic','model':'claude-sonnet-5-5','base_url':'https://api.anthropic.com/v1','key':KEY}
    assert mevan_ai.chat(config,{'messages':[{'role':'user','content':'U'}],'max_tokens':50,'temperature':0.1})=='Odgovor'
    capture(monkeypatch,{'content':[{'type':'thinking','thinking':'samo razmišljanje'}]})
    assert mevan_ai.test_connection(config) is True


def test_connection_check_explains_a_rejected_request_without_the_key(fx,monkeypatch):
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    def refused(request,timeout=None):
        body=json.dumps({'type':'error','error':{'type':'invalid_request_error','message':'temperature is not supported for this model; key '+KEY}}).encode()
        raise urllib.error.HTTPError(request.full_url,400,'Bad Request',{},io.BytesIO(body))
    monkeypatch.setattr(mevan_ai.urllib.request,'urlopen',refused)
    r=fx.client.post('/api/ai/test',headers=fx.headers)
    detail=r.json()['detail']
    assert r.status_code==502 and 'HTTP 400' in detail and 'temperature is not supported for this model' in detail
    assert KEY not in r.text and '[ključ]' in detail


def test_json_reply_is_extracted_from_surrounding_text_and_truncation_is_reported(monkeypatch):
    config={'provider':'anthropic','model':'claude-sonnet-5-5','base_url':'https://api.anthropic.com/v1','key':KEY}
    body={'messages':[{'role':'user','content':'U'}],'response_format':{'type':'json_object'},'max_tokens':50}
    capture(monkeypatch,{'content':[{'type':'text','text':'Evo nacrta:\n{"a": {"b": 2}}\nNadam se da pomaže.'}],'stop_reason':'end_turn'})
    assert json.loads(mevan_ai.chat(config,body))=={'a':{'b':2}}
    capture(monkeypatch,{'content':[{'type':'text','text':'{"a": [1, 2'}],'stop_reason':'max_tokens'})
    with pytest.raises(ValueError,match='prekinut zbog ograničenja dužine'):
        mevan_ai.chat(config,body)
    openai={'provider':'openai','model':'m','base_url':'https://api.openai.com/v1','key':KEY}
    capture(monkeypatch,{'choices':[{'message':{'content':'{"a": [1'},'finish_reason':'length'}]})
    with pytest.raises(ValueError,match='prekinut zbog ograničenja dužine'):
        mevan_ai.chat(openai,body)


def test_integrated_analysis_says_why_a_draft_was_rejected(fx,monkeypatch):
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    request={'company':{'name':'QA'},'assess':{'F01':{'applicable':'yes','score':'2','proof':'confirmed','evidence':'Dokaz','finding':'Nalaz'}},'effects':[]}
    capture(monkeypatch,{'content':[{'type':'text','text':'{"executive_summary": "Sažetak"}'}],'stop_reason':'end_turn'})
    r=fx.client.post('/api/v3/analyze',json=request,headers=fx.headers)
    assert r.status_code==502 and r.json()['detail'].endswith('Razlog: Nepotpuna AI analiza.'),r.text
    capture(monkeypatch,{'content':[{'type':'text','text':'{"executive_summary": "S'}],'stop_reason':'max_tokens'})
    assert 'prekinut zbog ograničenja dužine' in fx.client.post('/api/v3/analyze',json=request,headers=fx.headers).json()['detail']
    def slow(request,timeout=None):
        raise TimeoutError('timed out')
    monkeypatch.setattr(mevan_ai.urllib.request,'urlopen',slow)
    assert 'nije odgovorio na vrijeme' in fx.client.post('/api/v3/analyze',json=request,headers=fx.headers).json()['detail']
    assert 'v3_ai_draft_rejected' in fx.client.get('/api/audit').text


def _wait_for_job(client,job):
    import time
    for _ in range(100):
        state=client.get('/api/v3/analyze/job/'+job).json()
        if state.get('status')!='running':
            return state
        time.sleep(.05)
    raise AssertionError('posao nije završen')


def test_integrated_analysis_runs_as_a_background_job(fx,monkeypatch):
    import threading
    fx.client.put('/api/ai/settings',json=FORM,headers=fx.headers)
    request={'company':{'name':'QA'},'assess':{'F01':{'applicable':'yes','score':'2','proof':'confirmed','evidence':'Dokaz','finding':'Nalaz'}},'effects':[]}
    release=threading.Event()
    def slow_invalid(req,timeout=None):
        release.wait(5)
        return Reply({'content':[{'type':'text','text':'{"executive_summary": "Sažetak"}'}],'stop_reason':'end_turn'})
    monkeypatch.setattr(mevan_ai.urllib.request,'urlopen',slow_invalid)
    started=fx.client.post('/api/v3/analyze/start',json=request,headers=fx.headers)
    assert started.status_code==202
    job=started.json()['job']
    # Dok AI servis radi, server odgovara na druge zahtjeve (provjera zdravlja, stanje posla).
    assert fx.client.get('/api/v3/analyze/job/'+job).json()=={'status':'running'}
    assert fx.client.get('/health').json()=={'status':'ok'}
    release.set()
    state=_wait_for_job(fx.client,job)
    assert state['status']=='error' and state['code']==502 and state['detail'].endswith('Razlog: Nepotpuna AI analiza.')
    assert fx.client.get('/api/v3/analyze/job/'+job).status_code==404  # rezultat se čita jednom


def test_background_job_endpoints_are_protected(fx):
    request={'assess':{},'effects':[]}
    assert fx.client.post('/api/v3/analyze/start',json=request,headers={'Origin':'https://evil.example'}).status_code==403
    assert fx.client.post('/api/v3/analyze/start',content='nije json',headers={**fx.headers,'Content-Type':'application/json'}).status_code==400
    assert fx.client.get('/api/v3/analyze/job/nepostojeci').status_code==404
    fx.client.post('/logout',headers=fx.headers,follow_redirects=False)
    assert fx.client.get('/api/v3/analyze/job/nepostojeci').status_code==401
    assert fx.client.post('/api/v3/analyze/start',json=request,headers=fx.headers).status_code==401


def test_ai_calls_do_not_block_the_server_loop():
    from pathlib import Path
    source=(Path(mevan_ai.__file__).parent/'server.py').read_text(encoding='utf-8')
    # U async rutama svaki poziv AI servisa ide u zasebnu nit.
    assert source.count('await asyncio.to_thread(mevan_ai.chat,')==3
    assert 'return await asyncio.to_thread(_v3_analysis,data,rules)' in source
    assert source.count('mevan_ai.chat(ai,')==1  # jedini direktni poziv je unutar _v3_analysis, koja uvijek radi u niti


def test_finished_analysis_is_stored_in_the_diagnostic_and_resumed_after_leaving():
    from pathlib import Path
    html=(Path(mevan_ai.__file__).parent/'index.html').read_text(encoding='utf-8')
    # Rezultat se upisuje u dijagnostiku (ide u lokalnu kopiju i na server), ne samo u memoriju stranice.
    assert "target.v3={result:obj,source:ticket.signature,saved_at:new Date().toISOString()};" in html
    assert html.index("target.v3={result:obj")<html.index("save();",html.index("target.v3={result:obj"))<html.index("async function v3Wait(")
    # Oznaka pokrenutog posla se pamti, pa se rezultat preuzima i nakon zatvaranja stranice.
    assert "localStorage.setItem(V3_TICKET,JSON.stringify(ticket));" in html and "const pending=!v3Busy&&v3Ticket();if(pending){setTimeout(()=>v3Wait(pending),0)}" in html
    # Svaka dijagnostika prikazuje samo svoju analizu.
    assert "if(v3Owner===diagnostic.id&&!force)return;" in html and html.count("syncV3();")>=3
    assert "Podaci su od tada promijenjeni; pokrenite analizu ponovo da bude ažurna." in html


def test_workspace_with_a_stored_analysis_is_accepted_by_the_server(fx):
    stored={'result':{'analysis':{'executive_summary':'Sažetak'},'facts':{'index':36.4},'criteria':[]},'source':'potpis','saved_at':'2026-11-11T12:00:00.000Z'}
    workspace={'companies':[{'id':'c1','company':{'name':'QA'},'diagnostics':[{'id':'d1','name':'Dijagnostika','assess':{},'effects':[],'v3':stored}]}],
               'activeCompanyId':'c1','activeDiagnosticId':'d1'}
    version=fx.client.get('/api/workspace').json()['version']
    saved=fx.client.put('/api/workspace',json=workspace,headers={**fx.headers,'If-Match':version})
    assert saved.status_code==200,saved.text
    assert fx.client.get('/api/workspace').json()['workspace']['companies'][0]['diagnostics'][0]['v3']==stored


# ---- 11: razmišljanje, mjesečni limit, potrošnja i upozorenje o kreditima

def test_reasoning_level_is_saved_and_sent_only_to_claude(fx,monkeypatch):
    saved=fx.client.put('/api/ai/settings',json={**FORM,'effort':'low','monthly_limit':5},headers=fx.headers).json()
    assert saved['effort']=='low' and saved['monthly_limit']==5 and [e['id'] for e in saved['efforts']]==['','low','medium','high','xhigh']
    config=mevan_ai.active_config(fx.server.DB)
    seen=capture(monkeypatch,{'content':[{'type':'text','text':'ok'}],'usage':{'input_tokens':11,'output_tokens':7}})
    mevan_ai.chat(config,{'messages':[{'role':'user','content':'U'}],'max_tokens':20})
    assert json.loads(seen[0].data)['output_config']=={'effort':'low'}
    fx.client.put('/api/ai/settings',json={**FORM,'effort':''},headers=fx.headers)
    mevan_ai.chat(mevan_ai.active_config(fx.server.DB),{'messages':[{'role':'user','content':'U'}],'max_tokens':20})
    assert 'output_config' not in json.loads(seen[1].data)
    openai={**config,'provider':'openai','base_url':'https://api.openai.com/v1','effort':'low'}
    capture(monkeypatch,{'choices':[{'message':{'content':'ok'},'finish_reason':'stop'}]})
    seen=capture(monkeypatch,{'choices':[{'message':{'content':'ok'},'finish_reason':'stop'}]})
    mevan_ai.chat(openai,{'messages':[{'role':'user','content':'U'}],'max_tokens':20})
    assert 'output_config' not in json.loads(seen[0].data)
    assert fx.client.put('/api/ai/settings',json={**FORM,'effort':'najjace'},headers=fx.headers).status_code==422
    assert fx.client.put('/api/ai/settings',json={**FORM,'monthly_limit':-1},headers=fx.headers).status_code==422


def test_usage_is_counted_and_the_monthly_allowance_stops_further_calls(fx,monkeypatch):
    fx.client.put('/api/ai/settings',json={**FORM,'monthly_limit':2},headers=fx.headers)
    capture(monkeypatch,{'content':[{'type':'text','text':'Nacrt'}],'usage':{'input_tokens':100,'output_tokens':40}})
    draft={'dimension':'F','criteria':[{'code':'F01','name':'Profitabilnost','score':'2','proof':'confirmed','finding':'Nalaz','evidence':'Dokaz','kpi':'','recommendation':'','applicable':'yes','financial':''}],'financial_effects':[]}
    for _ in range(2):
        assert fx.client.post('/api/ai/draft',json=draft,headers=fx.headers).status_code==200
    usage=fx.client.get('/api/ai/settings').json()['usage']
    assert usage=={'calls':2,'input_tokens':200,'output_tokens':80}
    blocked=fx.client.post('/api/ai/draft',json=draft,headers=fx.headers)
    assert blocked.status_code==429 and 'mjesečni limit od 2 AI poziva' in blocked.json()['detail']
    # Integrisana analiza kao pozadinski posao javlja isti razlog.
    job=fx.client.post('/api/v3/analyze/start',json={'assess':{'F01':{'applicable':'yes','score':'2','proof':'confirmed','evidence':'Dokaz','finding':'Nalaz'}},'effects':[]},headers=fx.headers).json()['job']
    state=_wait_for_job(fx.client,job)
    assert state['status']=='error' and state['code']==429 and 'mjesečni limit' in state['detail']
    # Provjera veze radi i kad je limit dostignut; limit 0 znači bez ograničenja.
    assert fx.client.post('/api/ai/test',headers=fx.headers).status_code==200
    fx.client.put('/api/ai/settings',json={**FORM,'monthly_limit':0},headers=fx.headers)
    assert fx.client.post('/api/ai/draft',json=draft,headers=fx.headers).status_code==200


def test_existing_database_gets_the_new_columns(tmp_path):
    import sqlite3
    db=tmp_path/'staro.sqlite3'
    with sqlite3.connect(db) as connection:
        connection.execute('CREATE TABLE ai_settings (id INTEGER PRIMARY KEY CHECK(id=1), provider TEXT NOT NULL, model TEXT NOT NULL, base_url TEXT NOT NULL, key_cipher TEXT NOT NULL, key_hint TEXT NOT NULL, updated INTEGER NOT NULL)')
        connection.execute("INSERT INTO ai_settings VALUES(1,'anthropic','claude-sonnet-5-5','https://api.anthropic.com/v1','x','abcd',1)")
    public=mevan_ai.public_settings(db)
    assert public['effort']=='' and public['monthly_limit']==0 and public['usage']=={'calls':0,'input_tokens':0,'output_tokens':0}


def test_every_ai_button_warns_about_credits_first():
    from pathlib import Path
    root=Path(mevan_ai.__file__).parent
    index=(root/'index.html').read_text(encoding='utf-8')
    assert "async function runV3(){\n if(!await mvConfirmAiCost('Integrisana analiza'))return;" in index
    assert "async function makeAIDraft(dim){if(!await mvConfirmAiCost('AI nacrt'))return;" in index
    assert "if(!basic&&!await mvConfirmAiCost('AI projektni nacrt'))return;" in (root/'projects_ui.html').read_text(encoding='utf-8')
    import mevan_nav
    assert 'window.mvConfirmAiCost=async function(action){' in mevan_nav.JS and "okLabel:'Pokreni i potroši kredite'" in mevan_nav.JS


def test_shared_and_page_scripts_are_valid_javascript(tmp_path):
    """Sintaksna greška u zajedničkoj skripti gasi poruke, potvrde i prevod na svim ekranima."""
    import re,subprocess
    from pathlib import Path
    import mevan_nav
    root=Path(mevan_ai.__file__).parent
    sources={'nav':mevan_nav.JS}
    for name in ('index.html','projects_ui.html','dashboard_ui.html','diagnostic_review.html'):
        sources[name]=(root/name).read_text(encoding='utf-8')
    count=0
    for name,html in sources.items():
        for number,script in enumerate(re.findall(r'<script\b[^>]*>(.*?)</script>',html,re.S)):
            if not script.strip():continue
            path=tmp_path/f'{name}-{number}.js';path.write_text(script,encoding='utf-8')
            result=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
            assert result.returncode==0,(name,number,result.stderr[:400])
            count+=1
    assert count>=6
