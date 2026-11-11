from urllib.error import HTTPError
from io import BytesIO
import pytest
from remote_acceptance import validate_target, check

class Response:
    def __init__(self,status,location=''):
        self.status=status
        self.headers={'Location':location}
    def close(self):pass
class FakeOpener:
    def __init__(self,overrides=None):self.overrides=overrides or {}
    def open(self,req,timeout=10):
        path=req.full_url.split('example.invalid')[-1]
        return self.overrides.get(path, Response(200 if path=='/login' else 401 if path=='/api/workspace' else 303,'/login'))

def test_https_target_validation():
    assert validate_target('https://test.example.invalid/')=='https://test.example.invalid'
    for url in ('http://test.example.invalid','https://user:pass@test.example.invalid','https://test.example.invalid/other','https://localhost','https://test.example.invalid/?key=x'):
        with pytest.raises(ValueError):validate_target(url)

def test_anonymous_acceptance_success():
    assert all(ok for _,ok,_ in check('https://test.example.invalid',FakeOpener()))

def test_anonymous_data_leak_detected():
    results=check('https://test.example.invalid',FakeOpener({'/projects-ui':Response(200)}))
    assert not dict((path,ok) for path,ok,_ in results)['/projects-ui']

def test_anonymous_workspace_leak_detected():
    results=check('https://test.example.invalid',FakeOpener({'/api/workspace':Response(200)}))
    assert not dict((path,ok) for path,ok,_ in results)['/api/workspace']
