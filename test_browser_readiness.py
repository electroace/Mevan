"""HTTP-level browser readiness checks; not a real browser E2E test."""
import importlib, os, re, sys, tempfile
from pathlib import Path
from fastapi.testclient import TestClient


def test_ui_auth_navigation_and_assets():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ.update(MEVAN_ADMIN_EMAIL='demo@example.invalid',MEVAN_ADMIN_PASSWORD='local-demo-password-123',MEVAN_SESSION_SECRET='local-test-secret-0123456789-abcdefghijklmnopqrstuvwxyz',MEVAN_SECURE_COOKIE='0',MEVAN_DB=str(Path(tmp)/'mevan.sqlite3'))
        sys.modules.pop('server',None)
        app=importlib.import_module('server').app
        with TestClient(app,base_url='http://testserver') as client:
            for route in ('/','/projects-ui','/dashboard-ui'):
                r=client.get(route,follow_redirects=False)
                assert r.status_code in (302,303,307),route
                assert '/login' in r.headers['location']
            login=client.get('/login')
            csrf=re.search(r'name="csrf_token" value="([^"]+)"',login.text).group(1)
            r=client.post('/login',data={'csrf_token':csrf,'email':'demo@example.invalid','password':'local-demo-password-123'},headers={'Origin':'http://testserver'},follow_redirects=False)
            assert r.status_code==303
            for route in ('/','/projects-ui','/dashboard-ui'):
                r=client.get(route)
                assert r.status_code==200,route
                assert '<html' in r.text.lower() or '<!doctype' in r.text.lower(),route
                assert len(r.text)>1000,route
            assert client.get('/api/v4/dashboard').status_code==200
            assert client.get('/api/v4/projects').status_code==200
            assert client.post('/logout',headers={'Origin':'http://testserver'},follow_redirects=False).status_code==303
            assert client.get('/api/v4/dashboard').status_code==401
