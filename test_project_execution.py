"""Isolated v4 project workflow checks."""
import os, tempfile, unittest, importlib, sys, re
from pathlib import Path
from fastapi.testclient import TestClient

class TestProjectExecution(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  os.environ.update(MEVAN_ADMIN_EMAIL='demo@example.test',MEVAN_ADMIN_PASSWORD='A-new-safe-demo-password-123',MEVAN_SESSION_SECRET='s'*48,MEVAN_SECURE_COOKIE='0',MEVAN_DB=str(Path(self.tmp.name)/'test.sqlite3'))
  for mod in ('server','project_execution'):
   if mod in sys.modules:del sys.modules[mod]
  self.server=importlib.import_module('server')
  self.client=TestClient(self.server.app,base_url='http://testserver')
  token=re.search(r'name="csrf_token" value="([^"]+)"',self.client.get('/login').text).group(1)
  r=self.client.post('/login',data={'csrf_token':token,'email':'demo@example.test','password':'A-new-safe-demo-password-123'},follow_redirects=False)
  self.assertEqual(r.status_code,303)
  self.headers={'Origin':'http://testserver'}
  self.charter={'problem':'Simulirani problem bez nezavisne provjere','objective':'Prikupiti dokaze i validirati uzrok','scope':'Pilot','methodology':'DMAIC'}
 def tearDown(self):
  self.client.close();self.tmp.cleanup()
 def test_auth_origin_and_gate(self):
  payload={'company_id':'metalpro-demo','diagnostic_id':'demo-initial','title':'Provjera uzroka METALPRO','charter':self.charter}
  self.assertEqual(self.client.post('/api/v4/projects',json=payload).status_code,403)
  r=self.client.post('/api/v4/projects',json=payload,headers=self.headers)
  self.assertEqual(r.status_code,201)
  pid=r.json()['id']
  self.assertEqual(self.client.post('/api/v4/projects',json=payload,headers=self.headers).status_code,409)
  self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/approve-implementation',headers=self.headers).status_code,409)
  self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/approve-validation',headers=self.headers).status_code,200)
  ch=dict(self.charter,baseline_verified=True,targets_approved=True,checks_completed=True)
  self.assertEqual(self.client.put(f'/api/v4/projects/{pid}/charter',json=ch,headers=self.headers).status_code,200)
  self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/approve-implementation',headers=self.headers).status_code,200)
  self.assertEqual(self.client.put(f'/api/v4/projects/{pid}/charter',json=ch,headers=self.headers).status_code,409)
  review={'week':'2026-W46','note':'SIMULACIJA: samo provjera funkcije'}
  self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/weekly-reviews',json=review,headers=self.headers).status_code,201)
  self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/weekly-reviews',json=review,headers=self.headers).status_code,409)
  data=self.client.get(f'/api/v4/projects/{pid}').json()
  self.assertEqual(len(data['weekly_reviews']),1)
  self.assertEqual(data['status'],'implementation')
 def test_protected_without_login(self):
  self.client.post('/logout',headers=self.headers,follow_redirects=False)
  self.assertEqual(self.client.get('/api/v4/projects').status_code,401)
if __name__=='__main__':unittest.main()
