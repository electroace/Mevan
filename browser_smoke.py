"""Local Chromium smoke check. No production connection or external AI requests."""
import os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
PORT=18761
URL=f'http://127.0.0.1:{PORT}'
with tempfile.TemporaryDirectory(prefix='mevan-browser-') as tmp:
    env=os.environ.copy()
    env.update(MEVAN_ADMIN_EMAIL='demo@example.invalid', MEVAN_ADMIN_PASSWORD='local-demo-password-123', MEVAN_SESSION_SECRET='local-test-secret-0123456789-abcdefghijklmnopqrstuvwxyz', MEVAN_DB=str(Path(tmp)/'demo.sqlite3'))
    proc=subprocess.Popen([sys.executable,'-m','uvicorn','server:app','--host','127.0.0.1','--port',str(PORT)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for _ in range(80):
            if proc.poll() is not None: raise RuntimeError('Server stopped: '+proc.stderr.read().decode()[-1500:])
            try:
                urllib.request.urlopen(URL+'/login',timeout=1)
                break
            except Exception: time.sleep(.15)
        else: raise RuntimeError('Server did not start')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            page=browser.new_page()
            errors=[]
            page.on('pageerror',lambda error: errors.append(str(error)))
            page.goto(URL+'/projects-ui'); assert '/login' in page.url
            page.locator('input[name="email"]').fill('demo@example.invalid')
            page.locator('input[name="password"]').fill('local-demo-password-123')
            page.locator('button[type="submit"],button').first.click()
            page.wait_for_url(URL+'/',timeout=15000)
            for route in ('/','/projects-ui','/dashboard-ui'):
                resp=page.goto(URL+route,wait_until='domcontentloaded')
                page.wait_for_timeout(400)
                assert resp.status==200,(route,resp.status)
                assert '/login' not in page.url
                print('PASS authenticated browser route',route,'title=',page.title())
            assert not errors,'Browser JS errors: '+repr(errors)
            browser.close()
        print('PASS no uncaught JavaScript page errors')
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill()
