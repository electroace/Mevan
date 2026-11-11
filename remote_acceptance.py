"""Read-only acceptance probe for the isolated HTTPS test deployment.

Usage: python remote_acceptance.py https://your-test-host.example
No credentials required; never tests or modifies production data.
"""
import argparse
import ssl
import sys
from urllib.parse import urlsplit, urljoin
from urllib.request import build_opener, HTTPRedirectHandler, Request
from urllib.error import HTTPError, URLError

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None

def validate_target(url):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
        raise ValueError('Očekuje se isključivo HTTPS osnovna adresa bez korisničkih podataka, putanje ili parametara')
    if parsed.hostname in ('localhost','127.0.0.1','0.0.0.0'):
        raise ValueError('Ovaj test je namijenjen udaljenoj HTTPS testnoj instanci')
    return url.rstrip('/')

def check(base, opener=None):
    base=validate_target(base)
    opener=opener or build_opener(NoRedirect())
    checks=[]
    for path in ('/', '/projects-ui', '/dashboard-ui'):
        req=Request(base+path,headers={'User-Agent':'MEVAN-test-acceptance/1.0'})
        try:
            res=opener.open(req,timeout=10)
        except HTTPError as exc:
            res=exc
        except (URLError,TimeoutError) as exc:
            checks.append((path,False,'Nedostupno: '+str(exc)));continue
        status=res.status
        location=res.headers.get('Location','')
        # Unauthenticated routes must redirect to login, not disclose UI.
        ok=status in (302,303,307,308) and location in ('/login',base+'/login')
        checks.append((path,ok,f'HTTP {status}, Location: {location or "nema"}'))
        res.close()
    for path in ('/login','/api/workspace'):
        try:
            res=opener.open(Request(base+path),timeout=10)
        except HTTPError as exc:
            res=exc
        except (URLError,TimeoutError) as exc:
            checks.append((path,False,'Nedostupno: '+str(exc)));continue
        ok=(res.status==200) if path=='/login' else (res.status==401)
        checks.append((path,ok,f'HTTP {res.status}'))
        res.close()
    return checks

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url',help='HTTPS adresa ISKLJUČIVO testne instance')
    args=parser.parse_args()
    try:checks=check(args.url)
    except ValueError as exc:
        parser.error(str(exc))
    for path,ok,detail in checks:
        print(('PASS' if ok else 'FAIL'),path,detail)
    print('Ovaj test NE provjerava prijavu, AI, bazu, browser ni Docker; samo anonimni HTTPS pristup.')
    return 0 if all(ok for _,ok,_ in checks) else 1
if __name__=='__main__':sys.exit(main())
