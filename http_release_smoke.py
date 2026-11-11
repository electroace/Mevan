"""Isolated HTTP smoke test, no external API or production access."""
import os, re, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.request import build_opener, HTTPCookieProcessor, Request, HTTPRedirectHandler
from urllib.parse import urlencode
from urllib.error import HTTPError
from http.cookiejar import CookieJar

ROOT=Path(__file__).resolve().parent
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def main():
    with tempfile.TemporaryDirectory(prefix='mevan21-') as temp:
        import socket
        with socket.socket() as s:
            s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
        base=f'http://127.0.0.1:{port}'
        env=os.environ.copy()
        env.update(MEVAN_ADMIN_EMAIL='test@example.invalid',MEVAN_ADMIN_PASSWORD='local-smoke-only-password-123',MEVAN_SESSION_SECRET='smoke-session-secret-0123456789-abcdefghijklmnopqrstuvwxyz',MEVAN_SECURE_COOKIE='0',MEVAN_DB=str(Path(temp)/'smoke.sqlite3'),MEVAN_PUBLIC_ORIGIN=base,MEVAN_ALLOWED_HOSTS='127.0.0.1')
        proc=subprocess.Popen([sys.executable,'-m','uvicorn','server:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        opener=build_opener(HTTPCookieProcessor(CookieJar()),NoRedirect())
        def get(path):
            try:return opener.open(base+path,timeout=3)
            except HTTPError as ex:return ex
        try:
            for _ in range(100):
                if proc.poll() is not None:raise RuntimeError('Server failed to start: '+proc.stderr.read().decode()[-1000:])
                try:
                    if get('/login').status==200:break
                except Exception:time.sleep(.1)
            else:raise RuntimeError('Server startup timed out')
            for path in ('/','/projects-ui','/dashboard-ui'):
                response=get(path)
                assert response.status in (303,307) and response.headers.get('Location')=='/login',(path,response.status)
            assert get('/api/workspace').status==401
            login=get('/login').read().decode()
            token=re.search(r'name="csrf_token" value="([^"]+)"',login)
            assert token,'CSRF token missing'
            payload=urlencode({'csrf_token':token.group(1),'email':'test@example.invalid','password':'local-smoke-only-password-123'}).encode()
            try:response=opener.open(Request(base+'/login',data=payload,method='POST'),timeout=3)
            except HTTPError as ex:response=ex
            assert response.status==303 and response.headers.get('Location')=='/',response.status
            for path,marker in (('/','MEVAN'),('/projects-ui','MEVAN'),('/dashboard-ui','MEVAN')):
                response=get(path)
                html=response.read().decode()
                assert response.status==200 and marker in html,(path,response.status)
            assert get('/api/workspace').status==200
            print('PASS isolated HTTP login, session, protected screens, workspace API')
        finally:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill()
if __name__=='__main__':main()
