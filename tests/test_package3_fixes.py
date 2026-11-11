"""Paket 3: neispravan finansijski unos daje 422, a ocjena 0 ostaje vidljiva AI kontekstu."""
import json
import pytest
import test_project_execution as project_fixture


@pytest.fixture
def fx():
    fixture=project_fixture.TestProjectExecution(methodName='test_auth_origin_and_gate')
    fixture.setUp()
    try:
        yield fixture
    finally:
        fixture.tearDown()


def scenarios(count=3):
    names=('pesimistični','realni','optimistični')[:count]
    return {'scenarios':[{'name':n,'implementation_cost_km':'1000','annual_running_cost_km':'100',
        'benefits':[{'name':'Izbjegnuti trošak','category':'avoided_cost','amount_km':'500',
                     'source':'Simulirani ERP','assumption':'Procjena bez dokaza'}]} for n in names]}


def test_calculate_rejects_invalid_model_with_422(fx):
    r=fx.client.post('/api/v4/financial-scenarios/calculate',json=scenarios(2),headers=fx.headers)
    assert r.status_code==422,r.text
    assert 'scenarij' in r.json()['detail'].lower()
    r=fx.client.post('/api/v4/financial-scenarios/calculate',json={'scenarios':'x'},headers=fx.headers)
    assert r.status_code==422,r.text


def test_calculate_still_accepts_valid_model(fx):
    r=fx.client.post('/api/v4/financial-scenarios/calculate',json=scenarios(),headers=fx.headers)
    assert r.status_code==200,r.text
    assert len(r.json()['scenarios'])==3


def test_save_rejects_invalid_model_with_422_and_writes_nothing(fx):
    c=fx.client; h=fx.headers
    r=c.post('/api/v4/projects',json={'company_id':'paket3','diagnostic_id':'d1','title':'METALPRO provjera unosa','charter':fx.charter},headers=h)
    assert r.status_code==201,r.text
    base='/api/v4/projects/'+r.json()['id']
    bad=scenarios(); bad['scenarios'][0]['benefits'][0]['amount_km']='nije broj'
    r=c.put(base+'/financial-model',json=bad,headers=h)
    assert r.status_code==422,r.text
    assert c.get(base+'/financial-model').json()['model'] is None
    assert [e['action'] for e in c.get(base+'/audit').json()['events']]==['created']
    assert c.put(base+'/financial-model',json=scenarios(),headers=h).status_code==200


def test_v3_ai_context_keeps_numeric_zero_score(fx,monkeypatch):
    sent={}
    def fake_urlopen(request,timeout=None):
        sent['body']=json.loads(request.data.decode('utf-8'))
        raise ValueError('test ne poziva stvarni AI')
    monkeypatch.setenv('OPENAI_API_KEY','test-kljuc-nije-stvaran')
    monkeypatch.setattr(fx.server.urllib.request,'urlopen',fake_urlopen)
    assess={'O01':{'score':0,'proof':'confirmed','evidence':'Simulirani zapis'},
            'O02':{'score':'0','proof':'none'},
            'O03':{'score':3,'proof':'none'},
            'O04':{'score':None},'O05':{'score':''}}
    r=fx.client.post('/api/v3/analyze',json={'assess':assess,'effects':[]},headers=fx.headers)
    assert r.status_code==502,r.text
    context=json.loads(sent['body']['messages'][1]['content'])
    score={c['code']:c['score'] for c in context['criteria']}
    assert score['O01']=='0'
    assert score['O02']=='0'
    assert score['O03']=='3'
    assert score['O04']=='' and score['O05']==''
