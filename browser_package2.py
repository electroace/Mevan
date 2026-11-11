"""Mobilni sintetički tok paketa 2; koristi isključivo lokalni QA server na 8382."""
import io
import json
import os
from pathlib import Path
import subprocess

from docx import Document
from playwright.sync_api import sync_playwright

URL='http://127.0.0.1:8382'
OUT=Path(os.environ.get('MEVAN_QA_ARTIFACT_DIR','/tmp/mevan-package2-browser'))
OUT.mkdir(parents=True,exist_ok=True)

def open_menu(page):
    """Na telefonu je glavni meni iza dugmeta „Meni”."""
    toggle=page.locator('#mvToggle')
    if toggle.is_visible() and toggle.get_attribute('aria-expanded')!='true':
        toggle.click()


with sync_playwright() as pw:
    browser=pw.chromium.launch(args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    # Potvrde su prozori unutar aplikacije (#mvDialog); test ih prihvata kao ranije sistemske.
    page.add_init_script("setInterval(()=>{const d=document.getElementById('mvDialog');if(d&&d.open)d.querySelector('[value=ok]').click()},50)")
    page.goto(URL+'/login')
    page.locator('[name=email]').fill('qa@example.test');page.locator('[name=password]').fill('qa-local-only-test')
    page.locator('button').first.click();page.wait_for_url(URL+'/')
    page.wait_for_function('typeof serverVersion==="string"')
    open_menu(page);page.locator('[data-page=workspace]').click()
    page.get_by_role('button',name='Vrati METALPRO simulaciju',exact=True).click()
    page.wait_for_function('cloudStatus.includes("Sačuvano")')
    # Vođeni tok je dostupan i bez pozivanja AI servisa.
    open_menu(page);page.get_by_role('button',name='Vođeno prikupljanje i završni izvještaji',exact=True).click()
    page.wait_for_selector('#editor:not([hidden])')
    page.get_by_label('Način izvještaja').select_option('demo')
    page.get_by_role('button',name='Pripremi METALPRO DEMO primjer',exact=True).click()
    first=page.locator('details[data-code=F01]');first.locator('summary').click()
    notes={'interview':'DEMO intervju s finansijskim direktorom, 10.11.2026, ogledni zapis 17.',
           'documents':'DEMO dokument: ogledni P&L za Q3 2026, oznaka ERP-23.',
           'visit':'DEMO obilazak linije A, 10.11.2026, ilustrativni zapis 11.'}
    for stage,note in notes.items():
        assert page.locator('#guidedStage').input_value()==stage
        first.locator('[data-stage='+stage+'] textarea').fill(note)
        page.get_by_role('button',name='Sačuvaj i nastavi',exact=True).click()
        next_stage={'interview':'documents','documents':'visit','visit':'evidence'}[stage]
        page.wait_for_function('(stage)=>document.getElementById("guidedStage").value===stage&&!document.getElementById("editor").inert',arg=next_stage)
    page.reload();page.wait_for_selector('#editor:not([hidden])')
    assert page.locator('#guidedStage').input_value()=='evidence'
    loaded=page.request.get(URL+'/api/test/v2/workspace').json()
    company=next(c for c in loaded['workspace']['companies'] if c['id']=='metalpro-demo')
    diagnostic=next(d for d in company['diagnostics'] if d['id']=='demo-initial')
    assert next(r for r in diagnostic['quality_records'] if r['criterion_id']=='F01')['collection']==notes
    first=page.locator('details[data-code=F01]');first.locator('summary').click()
    first.get_by_label('Status dokaza',exact=True).select_option('nije_primjenjivo')
    first.get_by_label('Obrazloženje za N/P',exact=True).fill('U ovom oglednom obuhvatu proces nije primjenjiv jer se prikazuje zaseban operativni pilot.')
    first.get_by_role('button',name='Potvrdi N/P kao prijavljeni konsultant',exact=True).click()
    assert first.get_by_label('Ocjena 0–5 (prazno za N/P)',exact=True).input_value()==''
    assert first.get_by_label('N/P potvrdio konsultant',exact=True).input_value()=='qa@example.test'
    page.screenshot(path=str(OUT/'guided-evidence-na.png'),full_page=True)
    page.get_by_label('Korak vođenog prikupljanja').select_option('project')
    page.get_by_label('Prioritet za projekat',exact=True).select_option('C2')
    page.get_by_label('Vlasnik aktivnosti',exact=True).fill('QA voditelj kvaliteta')
    page.get_by_label('Početak plana',exact=True).fill('2026-11-10')
    page.get_by_label('KPI i način potvrde početnog stanja',exact=True).fill('Sati dorade po seriji — osnovicu potvrditi iz ogledne evidencije.')
    page.get_by_role('button',name='Sačuvaj odabrani projektni nacrt',exact=True).click()
    page.wait_for_selector('#projectLink a')
    page.reload();page.wait_for_selector('#projectLink a')
    page.get_by_label('Način izvještaja').select_option('real')
    page.get_by_role('button',name='Sačuvaj odabrani projektni nacrt',exact=True).click()
    page.wait_for_function('document.getElementById("notice").textContent.includes("drugačiji način")')
    page.get_by_label('Način izvještaja').select_option('demo')
    assert page.get_by_label('Prioritet za projekat',exact=True).input_value()=='C2'
    assert page.get_by_label('Vlasnik aktivnosti',exact=True).input_value()=='QA voditelj kvaliteta'
    state=page.request.get(URL+'/api/test/v2/workspace').json()['workspace']
    diagnostic=next(d for c in state['companies'] if c['id']=='metalpro-demo' for d in c['diagnostics'] if d['id']=='demo-initial')
    pid=diagnostic['guided']['project_id'];project_url=URL+'/api/v4/projects/'+pid
    project=page.request.get(project_url).json()
    assert project['status']=='draft' and project['charter']['report_mode']=='demo'
    assert len(project['charter']['activities'])==3 and project['charter']['activities'][-1]['due_date']=='2027-02-08'
    assert page.request.post(project_url+'/approve-implementation',headers={'Origin':URL}).status==409
    changed={**project['charter'],'report_mode':'real'}
    assert page.request.put(project_url+'/charter',data=changed,headers={'Origin':URL}).status==409
    page.get_by_label('Korak vođenog prikupljanja').select_option('plan')
    page.screenshot(path=str(OUT/'guided-plan.png'),full_page=True)
    page.get_by_role('button',name='Zaključi DEMO snimak',exact=True).click()
    page.wait_for_function('document.getElementById("notice").textContent.includes("snimak je zaključan")')
    approvals=page.request.get(URL+'/api/test/v2/approvals').json()
    approval=next(a for a in approvals if a['diagnostic_id']=='demo-initial')
    assert approval['report_mode']=='demo'
    aid=approval['approval_id']
    for view in ('executive','detailed'):
        for fmt in ('pdf','docx'):
            # URL parametar ne mijenja eksplicitni način zaključanog snimka.
            response=page.request.get(f'{URL}/api/test/v2/approvals/{aid}/{view}/{fmt}?mode=real')
            assert response.ok,response.text()
            path=OUT/f'package2_DEMO_{view}.{fmt}';path.write_bytes(response.body())
            if fmt=='docx':
                word=Document(io.BytesIO(response.body()))
                text='\n'.join(p.text for p in word.paragraphs)
                assert 'DEMO — simulirani podaci' in word.sections[0].header.paragraphs[0].text
                assert len(word.inline_shapes)==1
            else:
                text=subprocess.check_output(['pdftotext',str(path),'-']).decode()
                assert all('DEMO — simulirani podaci' in p for p in text.split('\f') if p.strip())
            assert 'DEMO — simulirani podaci' in text and 'Primjenjivo 60/61' in text and 'C2' in text
            assert 'U ovom oglednom obuhvatu' in text
            if view=='detailed':assert all(' '.join(note.split()) in ' '.join(text.split()) for note in notes.values())
    page.get_by_label('Način izvještaja').select_option('real')
    page.get_by_role('button',name='Odobri pregledanu reviziju',exact=True).click()
    page.wait_for_function('document.getElementById("notice").textContent.includes("Simulirani ulazi")')
    assert len(page.request.get(URL+'/api/test/v2/approvals').json())==len(approvals)
    page.get_by_label('Način izvještaja').select_option('demo')
    page.get_by_role('button',name='Sačuvaj radnu reviziju',exact=True).click()
    page.wait_for_function('!document.getElementById("editor").inert')
    page.screenshot(path=str(OUT/'guided-demo-final.png'),full_page=True)
    page.goto(URL+'/');page.wait_for_function('typeof serverVersion==="string"&&cloudStatus.includes("pregledana")')
    assert page.evaluate('summary(CRITERIA).app')==60
    assert page.evaluate('summary(CRITERIA).avg') is not None
    assert 'DEMO — simulirani podaci' in page.locator('#modeBanner').inner_text()
    for detailed in (False,True):
        with page.expect_popup() as popup:
            page.evaluate('(detailed)=>openReport("ALL",detailed)',detailed)
        preview=popup.value
        assert 'DEMO — simulirani podaci' in preview.locator('body').inner_text()
        assert 'U ovom oglednom obuhvatu' in preview.locator('body').inner_text()
        preview.close()
    with page.expect_download() as legacy_download:
        page.evaluate('exportDOCX("ALL",false)')
    legacy_path=OUT/'package2_DEMO_legacy.docx';legacy_download.value.save_as(legacy_path)
    legacy_text='\n'.join(p.text for p in Document(legacy_path).paragraphs)
    assert 'DEMO — simulirani podaci' in legacy_text and 'U ovom oglednom obuhvatu' in legacy_text
    open_menu(page);page.get_by_role('button',name='Vođeno prikupljanje i završni izvještaji',exact=True).click()
    page.wait_for_selector('#editor:not([hidden])')
    assert page.request.get(URL+'/api/test/v2/workspace').json()['workspace']['companies']
    assert not errors,errors
    (OUT/'package2-browser.json').write_text(json.dumps({'collection':notes,'project_id':pid,'project_status':project['status'],'approval_id':aid,'report_mode':'demo','applicable':60,'na':1,'outputs':4,'javascript_errors':errors},ensure_ascii=False,indent=2))
    print('Paket 2 mobilni tok: intervju → dokumenti → obilazak trajno sačuvani; N/P potvrđen; C2 povezan s projektnim nacrtom i planom 90 dana; četiri označena DEMO izvoza; stvarno odobrenje simulacije odbijeno.')
    browser.close()
