from playwright.sync_api import sync_playwright
import json, os, pathlib, sys
sys.path.insert(0,str(pathlib.Path.cwd()/'tests'))
from test_approved_delivery import diagnostic, review_content
from project_planner import FACTORS
from docx import Document
from subprocess import check_output
from io import BytesIO
artifacts=pathlib.Path(os.environ['MEVAN_QA_ARTIFACT_DIR']) if os.environ.get('MEVAN_QA_ARTIFACT_DIR') else None
if artifacts:artifacts.mkdir(parents=True,exist_ok=True)
with sync_playwright() as w:
 b=w.chromium.launch(args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto('http://127.0.0.1:8382/');p.locator('[name=email]').fill('qa@example.test');p.locator('[name=password]').fill('qa-local-only-test');p.locator('button').first.click();p.wait_for_url('**/');p.wait_for_function('typeof serverVersion==="string"')
 d=diagnostic('QA-mobile');d.update(name='QA provjera',plan=[],approved={},assess={r['criterion_id']:dict(score=r['score'],proof='confirmed',evidence='QA dokaz') for r in d['quality_records']})
 d['consultant_review']['summary']=''
 ws={'schema':3,'activeCompanyId':'qa','activeDiagnosticId':d['id'],'companies':[{'id':'qa','company':{'name':'QA čelik'},'diagnostics':[d]}]}
 url='http://127.0.0.1:8382'
 get=lambda path:p.request.get(url+path)
 headers={'Origin':url,'If-Match':get('/api/workspace').json()['version']}
 r=p.request.put(url+'/api/workspace',data=ws,headers=headers);assert r.ok,r.text()
 stale=p.request.put(url+'/api/workspace',data={'companies':[{'diagnostics':[]}]},headers=headers);assert stale.status==409
 p.reload();p.locator('#mvToggle').click();p.locator('[data-page=v2]').first.click()
 p.route('**/api/v3/analyze', lambda route:route.fulfill(json={'analysis':{'executive_summary':'QA prijedlog','decisions':[]},'criteria':[],'facts':{}}))
 p.get_by_role('button',name='Pokreni kompletnu dijagnostiku').click()
 p.wait_for_function('v3Result !== null')
 p.get_by_role('button',name='Konsultantska provjera i završni izvještaji').click();p.wait_for_selector('#editor:not([hidden])')
 assert p.locator('details').count()==61
 p.get_by_label('Korak vođenog prikupljanja').select_option('priorities');p.get_by_role('button',name='Preuzmi AI prijedlog za pregled').click()
 assert p.get_by_label('Izvršni sažetak').input_value()=='QA prijedlog'
 assert p.get_by_label('Prvi prioritet i dokaz').input_value()==review_content('QA-mobile')['priority1']
 p.on('dialog',lambda d:d.accept())
 labels={'summary':'Izvršni sažetak','priority1':'Prvi prioritet i dokaz','priority2':'Drugi prioritet i dokaz','priority3':'Treći prioritet i dokaz','month1':'1–30 dana · aktivnost, vlasnik, KPI i rok','month2':'31–60 dana · aktivnost, vlasnik, KPI i rok','month3':'61–90 dana · aktivnost, vlasnik, KPI i rok'}
 for key,label in labels.items():
  p.get_by_label('Korak vođenog prikupljanja').select_option('plan' if key.startswith('month') else 'priorities');p.get_by_label(label).fill('x')
 p.get_by_role('button',name='Odobri pregledanu reviziju').click()
 p.wait_for_function('document.getElementById("notice").textContent.includes("tehnička provjera")')
 assert p.locator('#downloads a').count()==0
 if artifacts:p.screenshot(path=str(artifacts/'mobile-review-rejected.png'),full_page=True)
 for key,label in labels.items():
  p.get_by_label('Korak vođenog prikupljanja').select_option('plan' if key.startswith('month') else 'priorities');p.get_by_label(label).fill(review_content('QA-mobile')[key])
 p.get_by_role('button',name='Odobri pregledanu reviziju').click();p.wait_for_selector('#downloads a')
 if artifacts:p.screenshot(path=str(artifacts/'mobile-review-approved.png'),full_page=True)
 for link in p.locator('#downloads a').all()[:4]:
  with p.expect_download() as ev:link.click()
  download=ev.value;path=download.path()
  if artifacts:download.save_as(str(artifacts/download.suggested_filename))
  if download.suggested_filename.endswith('pdf'):t=check_output(['pdftotext',str(path),'-']).decode()
  else:t='\n'.join(x.text for x in Document(path).paragraphs)
  assert 'Za dijagnostiku QA-mobile' in t and 'QA čelik' in t,(download.suggested_filename,t[:200])
 factors=['profit','liquidity','delivery','risk','feasibility']
 body={'company_id':'qa','diagnostic_id':'QA-mobile','expected_revision':0,'analysis':{'decisions':[{'title':'Kandidat '+str(i)} for i in range(1,4)]},'ratings':{}}
 for i,values in enumerate([[4,3,5,4,4],[4,2,3,4,4],[3,5,3,4,3]],1):
  body['ratings']['C'+str(i)]={k:{'value':str(v),'evidence':'','rationale':'Simulacija za tehnički test'} for k,v in zip(factors,values)}
 save=p.request.put(url+'/api/v4/candidate-drafts',data=body,headers={'Origin':url});assert save.ok,save.text()
 r=get('/api/v4/candidate-drafts?company_id=qa&diagnostic_id=QA-mobile').json()
 assert [i['score'] for i in r['draft']['ranking']]==[81,72,67],r
 p.goto(url+'/projects-ui');p.locator('#newCompany').fill('qa');p.locator('#newDiagnostic').fill('QA-mobile');p.get_by_role('button',name='Učitaj ocjene sa servera').click();p.wait_for_selector('#rankingResults li');assert p.locator('#rankingResults li').all_text_contents()==['C1 · 81/100','C3 · 72/100','C2 · 67/100']
 charter=dict(problem='Izolovana provjera unosa finansijskog efekta',objective='Provjeriti ponavljanje zahtjeva bez dupliranja',scope='QA pilot',methodology='DMAIC')
 r=p.request.post(url+'/api/v4/projects',data=dict(company_id='qa',diagnostic_id='qa-effects',title='QA finansijski efekat',charter=charter),headers={'Origin':url});assert r.ok,r.text()
 pid=r.json()['id'];base=url+'/api/v4/projects/'+pid
 charter.update(baseline_verified=True,targets_approved=True,checks_completed=True)
 assert p.request.put(base+'/charter',data=charter,headers={'Origin':url}).ok
 assert p.request.post(base+'/approve-implementation',headers={'Origin':url}).ok
 p.get_by_role('button',name='Osvježi',exact=True).click()
 p.get_by_role('button',name='QA finansijski efekat · implementation',exact=True).click();p.wait_for_selector('#actualPanel:not([hidden])')
 for field,value in dict(actualPeriod='2026-11',actualName='Smanjenje škarta',actualAmount='4000',actualEvidence='QA-racun-1',actualOwner='Kontroling',actualCalculation='Razlika troškova škarta za isti period').items():p.locator('#'+field).fill(value)
 p.locator('#actualConfirmed').check()
 p.get_by_role('button',name='Evidentiraj efekat',exact=True).click()
 p.wait_for_function('document.querySelectorAll("#actualEntries .panel").length===1')
 p.get_by_role('button',name='Evidentiraj efekat',exact=True).click()
 p.wait_for_function('document.getElementById("notice").textContent.includes("već evidentiran")')
 assert p.locator('#actualEntries .panel').count()==1
 assert p.request.get(base+'/actual-effects').json()['summary']['consultant_confirmed_recurring_km']==4000
 if artifacts:p.screenshot(path=str(artifacts/'mobile-effect-replayed.png'),full_page=True)
 # Explicitly different event, even with identical amounts and evidence.
 p.get_by_label('Oznaka zasebnog događaja (opcionalno)').fill('drugi-stvarni-dogadjaj')
 p.get_by_role('button',name='Evidentiraj efekat',exact=True).click()
 p.wait_for_function('document.querySelectorAll("#actualEntries .panel").length===2')
 assert not errors,errors
 print('Mobilni tok: x odbijen u sedam polja, valjan pregled odobren, četiri izvoza pročitana, C1/C3/C2 vraćen; stara revizija odbijena; 4000 KM ponovljeno ostaje jedan efekat, zaseban događaj sačuvan.')
