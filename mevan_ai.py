"""Izbor AI servisa i API ključ koji administrator unosi sam.

Ključ se čuva šifrovan u bazi (Fernet; ključ šifre izveden je iz MEVAN_SESSION_SECRET), ne vraća se
u preglednik i nije dio JSON sigurnosnih kopija. Šifrovanje štiti od curenja datoteke baze ili kopije;
ne štiti ako je kompromitovan sam server, jer je tajna na istom serveru. Ako se MEVAN_SESSION_SECRET
promijeni, ključ se više ne može pročitati i treba ga unijeti ponovo.
Bez unesenog ključa i dalje vrijede varijable okruženja OPENAI_API_KEY i MEVAN_AI_MODEL.
"""
import base64
import hashlib
import ipaddress
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROVIDERS = {
    'openai': {'label': 'ChatGPT (OpenAI)', 'base_url': 'https://api.openai.com/v1', 'model_hint': 'npr. gpt-4.1-mini'},
    'anthropic': {'label': 'Claude (Anthropic)', 'base_url': 'https://api.anthropic.com/v1', 'model_hint': 'npr. claude-sonnet-5-5'},
    'compatible': {'label': 'Drugi servis (OpenAI-kompatibilan API)', 'base_url': '', 'model_hint': 'naziv modela kod tog servisa'},
}
DEFAULT_OPENAI_MODEL = 'gpt-4.1-mini'
ANTHROPIC_VERSION = '2023-06-01'
# Noviji Claude modeli razmišljaju prije odgovora i to troše iz max_tokens; rezerva čuva prostor za sam odgovor.
ANTHROPIC_THINKING_HEADROOM = 4096
JSON_ONLY = ' Odgovori isključivo jednim JSON objektom, bez teksta prije ili poslije i bez oznaka koda.'


class SettingsError(ValueError):
    """Poruka je namijenjena korisniku; nikada ne sadrži ključ."""


def db_path():
    return Path(os.getenv('MEVAN_DB', str(Path(__file__).parent / 'mevan.sqlite3')))


def _connect(db=None):
    connection = sqlite3.connect(db or db_path())
    connection.execute('CREATE TABLE IF NOT EXISTS ai_settings (id INTEGER PRIMARY KEY CHECK(id=1), provider TEXT NOT NULL, '
                       'model TEXT NOT NULL, base_url TEXT NOT NULL, key_cipher TEXT NOT NULL, key_hint TEXT NOT NULL, updated INTEGER NOT NULL)')
    return connection


def _cipher():
    try:
        from cryptography.fernet import Fernet
    except ImportError as error:  # paket dolazi iz requirements; poruka kaže šta nedostaje
        raise SettingsError('Na serveru nedostaje paket cryptography. Ponovo pokrenite instalaciju zavisnosti.') from error
    secret = os.getenv('MEVAN_SESSION_SECRET', '')
    if len(secret) < 32:
        raise SettingsError('MEVAN_SESSION_SECRET nije postavljen; ključ se ne može sigurno sačuvati.')
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(('mevan-ai-key|' + secret).encode()).digest()))


def _valid_base_url(value):
    parsed = urllib.parse.urlsplit(value)
    host = (parsed.hostname or '').lower()
    if parsed.scheme != 'https' or not host or parsed.username or parsed.password or parsed.query or parsed.fragment or len(value) > 200:
        raise SettingsError('Adresa servisa mora biti puna https adresa bez korisničkog imena i parametara.')
    if host == 'localhost' or host.endswith('.local') or host.endswith('.internal'):
        raise SettingsError('Adresa servisa mora biti javni servis, ne lokalna adresa.')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise SettingsError('Adresa servisa mora biti javni servis, ne lokalna adresa.')
    return value.rstrip('/')


def save_settings(provider, model, base_url='', api_key='', db=None):
    """Sačuvaj izbor servisa. Prazan ključ zadržava postojeći, ali samo za isti servis i adresu."""
    provider, model, base_url, api_key = str(provider or ''), str(model or '').strip(), str(base_url or '').strip(), str(api_key or '').strip()
    if provider not in PROVIDERS:
        raise SettingsError('Nepoznat AI servis.')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,99}', model):
        raise SettingsError('Unesite naziv modela (slova, cifre i znakovi . _ : / -).')
    base_url = _valid_base_url(base_url) if provider == 'compatible' else PROVIDERS[provider]['base_url']
    with _connect(db) as connection:
        current = connection.execute('SELECT provider, base_url, key_cipher, key_hint FROM ai_settings WHERE id=1').fetchone()
        if api_key:
            if not re.fullmatch(r'[\x21-\x7e]{16,400}', api_key):
                raise SettingsError('API ključ nije u očekivanom obliku (16–400 znakova, bez razmaka).')
            cipher, hint = _cipher().encrypt(api_key.encode()).decode(), api_key[-4:]
        elif current and current[0] == provider and current[1] == base_url:
            cipher, hint = current[2], current[3]
        else:
            raise SettingsError('Unesite API ključ za odabrani servis.')
        connection.execute('INSERT INTO ai_settings(id,provider,model,base_url,key_cipher,key_hint,updated) VALUES(1,?,?,?,?,?,?) '
                           'ON CONFLICT(id) DO UPDATE SET provider=excluded.provider,model=excluded.model,base_url=excluded.base_url,'
                           'key_cipher=excluded.key_cipher,key_hint=excluded.key_hint,updated=excluded.updated',
                           (provider, model, base_url, cipher, hint, int(time.time())))
    return public_settings(db)


def clear_settings(db=None):
    with _connect(db) as connection:
        connection.execute('DELETE FROM ai_settings')
    return public_settings(db)


def _stored(db=None):
    with _connect(db) as connection:
        return connection.execute('SELECT provider, model, base_url, key_cipher, key_hint, updated FROM ai_settings WHERE id=1').fetchone()


def public_settings(db=None):
    """Ono što preglednik smije vidjeti: bez ključa, samo zadnja četiri znaka."""
    row = _stored(db)
    providers = [{'id': key, 'label': item['label'], 'model_hint': item['model_hint']} for key, item in PROVIDERS.items()]
    if row:
        return {'source': 'app', 'provider': row[0], 'model': row[1], 'base_url': row[2] if row[0] == 'compatible' else '',
                'key_set': True, 'key_hint': row[4], 'updated': row[5], 'providers': providers}
    if os.getenv('OPENAI_API_KEY', '').strip():
        return {'source': 'environment', 'provider': 'openai', 'model': os.getenv('MEVAN_AI_MODEL', DEFAULT_OPENAI_MODEL), 'base_url': '',
                'key_set': True, 'key_hint': '', 'updated': None, 'providers': providers}
    return {'source': 'none', 'provider': 'openai', 'model': '', 'base_url': '', 'key_set': False, 'key_hint': '', 'updated': None, 'providers': providers}


def active_config(db=None):
    """Postavke za poziv servisa ili None ako AI nije podešen. Uneseni ključ ima prednost nad okruženjem."""
    row = _stored(db)
    if row:
        try:
            key = _cipher().decrypt(row[3].encode()).decode()
        except Exception:  # promijenjena tajna ili oštećen zapis: ponaša se kao da ključ nije unesen
            return None
        return {'provider': row[0], 'model': row[1], 'base_url': row[2], 'key': key}
    key = os.getenv('OPENAI_API_KEY', '').strip()
    if key:
        return {'provider': 'openai', 'model': os.getenv('MEVAN_AI_MODEL', DEFAULT_OPENAI_MODEL), 'base_url': PROVIDERS['openai']['base_url'], 'key': key}
    return None


def chat(config, body, timeout=60, limit=200000):
    """Pošalji zahtjev u OpenAI obliku odabranom servisu i vrati tekst odgovora.

    Mrežne greške (urllib.error) i neispravan oblik odgovora (KeyError, ValueError) prolaze dalje,
    kao i ranije, da ih pozivalac pretvori u poruku za korisnika.
    """
    wants_json = (body.get('response_format') or {}).get('type') == 'json_object'
    if config['provider'] == 'anthropic':
        system = '\n\n'.join(m['content'] for m in body['messages'] if m['role'] == 'system')
        # Bez temperature: noviji Claude modeli odbijaju svaku vrijednost osim zadane (HTTP 400).
        payload = {'model': config['model'], 'max_tokens': body.get('max_tokens', 1024) + ANTHROPIC_THINKING_HEADROOM,
                   'messages': [{'role': m['role'], 'content': m['content']} for m in body['messages'] if m['role'] != 'system']}
        if system or wants_json:
            payload['system'] = system + (JSON_ONLY if wants_json else '')
        url, headers = config['base_url'] + '/messages', {'x-api-key': config['key'], 'anthropic-version': ANTHROPIC_VERSION}
    else:
        payload = {**body, 'model': config['model']}
        url, headers = config['base_url'] + '/chat/completions', {'Authorization': 'Bearer ' + config['key']}
    request = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                                     headers={**headers, 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        answer = json.loads(response.read(limit))
    if config['provider'] == 'anthropic':
        text = ''.join(block['text'] for block in answer['content'] if block.get('type') == 'text')
    else:
        text = answer['choices'][0]['message']['content']
    if not isinstance(text, str):
        raise ValueError('Neispravan odgovor AI servisa')
    if wants_json:
        text = re.sub(r'^\s*```(?:json)?\s*|\s*```\s*$', '', text)
    return text


def test_connection(config):
    """Kratak poziv odabranom servisu; uspjeh znači da servis prihvata ključ, model i oblik zahtjeva."""
    chat(config, {'messages': [{'role': 'user', 'content': 'Odgovori samo riječju: OK'}], 'max_tokens': 16}, timeout=40, limit=50000)
    return True


def error_detail(error, key=''):
    """Kratko objašnjenje iz odgovora servisa (polje error.message), bez ključa. Prazno ako ga nema."""
    try:
        body = json.loads(error.read(20000))
        message = body['error']['message'] if isinstance(body.get('error'), dict) else ''
    except Exception:
        return ''
    if not isinstance(message, str):
        return ''
    message = ' '.join(message.split())
    if key:
        message = message.replace(key, '[ključ]')
    return message[:240]
