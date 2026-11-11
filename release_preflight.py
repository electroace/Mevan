"""Offline deployment preflight; never prints environment secrets."""
from pathlib import Path
import os
import re
import sys

ROOT = Path(__file__).resolve().parent
REQUIRED = ["server.py", "index.html", "diagnostic_engine.py", "projects_ui.html", "dashboard_ui.html", "project_execution.py", "project_planner.py", "project_candidates.py", "project_ai_pack.py", "project_finance.py", "project_actuals.py", "project_reports.py"]

def check_bundle():
    errors = []
    dockerfile = (ROOT / "Dockerfile").read_text()
    for filename in REQUIRED:
        if not (ROOT / filename).is_file():
            errors.append(f"Nedostaje: {filename}")
        if filename.startswith('project_'):
            if 'project_*.py' not in dockerfile and filename not in dockerfile:
                errors.append(f"Dockerfile ne uključuje: {filename}")
        elif filename not in dockerfile:
            errors.append(f"Dockerfile ne uključuje: {filename}")
    compose = (ROOT / 'compose.yaml').read_text()
    if '127.0.0.1:8000:8000' not in compose:
        errors.append('Docker port nije ograničen na localhost')
    if 'MEVAN_DB: /data/mevan.sqlite3' not in compose:
        errors.append('Nije definisana trajna putanja baze')
    return errors

def check_runtime():
    errors = []
    for key, minimum in [('MEVAN_ADMIN_PASSWORD', 16), ('MEVAN_SESSION_SECRET', 32)]:
        val = os.getenv(key, '')
        if len(val) < minimum or any(x in val.upper() for x in ('POSTAVI_', 'GENERISI_', 'PLACEHOLDER', 'CHANGE_ME')):
            errors.append(f'{key} nije postavljen na sigurnu vrijednost')
    origin = os.getenv('MEVAN_PUBLIC_ORIGIN', '')
    if not origin.startswith('https://') or 'example' in origin:
        errors.append('MEVAN_PUBLIC_ORIGIN mora biti stvarna HTTPS testna adresa')
    hosts = os.getenv('MEVAN_ALLOWED_HOSTS', '')
    if not hosts or 'example' in hosts or '*' in hosts:
        errors.append('MEVAN_ALLOWED_HOSTS mora ograničiti stvarni testni host')
    if os.getenv('MEVAN_SECURE_COOKIE') != '1':
        errors.append('MEVAN_SECURE_COOKIE mora biti 1')
    return errors

if __name__ == '__main__':
    errors = check_bundle()
    if '--runtime' in sys.argv:
        errors.extend(check_runtime())
    for err in errors:
        print('FAIL:', err)
    if errors:
        sys.exit(1)
    print('OK: lokalna provjera paketa' + (' i postavki' if '--runtime' in sys.argv else '') + ' prošla')
