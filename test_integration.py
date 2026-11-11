"""Offline integration tests: python -m unittest -v test_integration.py"""
import os,tempfile,unittest,importlib,sys
from pathlib import Path
from fastapi.testclient import TestClient
import re

class TestMevan(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory()
  os.environ.update(MEVAN_ADMIN_EMAIL='demo@example.test',MEVAN_ADMIN_PASSWORD='A-new-safe-demo-password-123',MEVAN_SESSION_SECRET='s'*48,MEVAN_SECURE_COOKIE='0',MEVAN_DB=str(Path(cls.tmp.name)/'test.sqlite3'))
  if 'server' in sys.modules:del sys.modules['server']
  cls.server=importlib.import_module('server')
  cls.client=TestClient(cls.server.app,base_url='http://testserver')
 @classmethod
 def tearDownClass(cls):cls.client.close();cls.tmp.cleanup()
 def test_01_protected(self):
  self.assertEqual(self.client.get('/api/workspace').status_code,401)
  self.assertEqual(self.client.post('/api/ai/draft',json={}).status_code,401)
 def test_02_login_and_persistence(self):
  token=re.search(r'name="csrf_token" value="([^"]+)"',self.client.get('/login').text).group(1)
  bad=self.client.post('/login',data={'csrf_token':token,'email':'demo@example.test','password':'wrong'},headers={'Origin':'http://testserver'},follow_redirects=False)
  self.assertEqual(bad.status_code,401)
  good=self.client.post('/login',data={'csrf_token':token,'email':'demo@example.test','password':'A-new-safe-demo-password-123'},headers={'Origin':'http://testserver'},follow_redirects=False)
  self.assertEqual(good.status_code,303)
  payload={'companies':[{'name':'METALPRO DEMO','diagnostics':[]}]}
  self.assertEqual(self.client.put('/api/workspace',json=payload,headers={'Origin':'http://testserver'}).status_code,200)
  self.assertEqual(self.client.get('/api/workspace').json()['workspace'],payload)
  self.assertEqual(self.client.put('/api/workspace',json=payload,headers={'Origin':'https://evil.test'}).status_code,403)
  self.assertEqual(self.client.put('/api/workspace',json={'companies':[]},headers={'Origin':'http://testserver'}).status_code,400)
 def test_02b_backup_restore_and_audit(self):
  backup=self.client.get('/api/backup')
  self.assertEqual(backup.status_code,200)
  self.assertEqual(backup.json()['format'],'mevan-backup-v1')
  self.assertEqual(backup.json()['workspace']['companies'][0]['name'],'METALPRO DEMO')
  headers={'Origin':'http://testserver','X-MEVAN-Confirm-Restore':'VRATI-PODATKE'}
  self.assertEqual(self.client.post('/api/backup/restore',json=backup.json(),headers={'Origin':'http://testserver'}).status_code,400)
  self.assertEqual(self.client.post('/api/backup/restore',json={'format':'bad'},headers=headers).status_code,400)
  self.assertEqual(self.client.post('/api/backup/restore',json=backup.json(),headers=headers).status_code,200)
  self.assertEqual(self.client.get('/api/workspace').json()['workspace'],backup.json()['workspace'])
  events=self.client.get('/api/audit').json()['events']
  self.assertTrue(any(e['event']=='backup_restore' for e in events))
 def test_03_ai_without_key_and_logout(self):
  os.environ.pop('OPENAI_API_KEY',None)
  r=self.client.post('/api/ai/draft',json={'dimension':'O','criteria':[]},headers={'Origin':'http://testserver'})
  self.assertEqual(r.status_code,503)
  self.assertEqual(self.client.post('/logout',headers={'Origin':'https://evil.test'},follow_redirects=False).status_code,403)
  self.assertEqual(self.client.post('/logout',headers={'Origin':'http://testserver'},follow_redirects=False).status_code,303)
  self.assertEqual(self.client.get('/api/workspace').status_code,401)

if __name__=='__main__':unittest.main()
