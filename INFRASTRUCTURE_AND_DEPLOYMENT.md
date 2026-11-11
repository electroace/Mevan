> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: runtime, verzije, env ugovor, lokalni setup, backup, CI i hosting razlike.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — infrastruktura, zavisnosti i pokretanje

## Šta je aktivno, opcionalno i nepostojeće

Aktivni lokalni stack: Python/FastAPI/uvicorn, statički HTML/CSS/JS, sqlite3, python-docx, ReportLab, DejaVu i Pillow. Nema npm frontend builda/package.json niti React/Vue/Angular aplikacije. Node služi Word QA, Playwright/Chromium služi browser provjeri, Poppler čitanju/renderu PDF-a. Optional: OpenAI API kroz urllib; psycopg samo candidate-drafts. Declared hosting materijal: Dockerfile/Compose za izolovanu instancu. Nema Cloudflare Workers/D1, Supabase, e-mail provajdera, Stripe/billing, OAuth/OIDC ili vanjskog auth servisa u ovom kodu.

## Lokalno, GitHub i hosting su tri različita stanja

| Površina | Zabilježena verzija | Dokaz / granica |
|---|---|---|
| Lokalni kod | `132ef288917b0573709655437cb8904574898015` | Ponovo read-only potvrđeni HEAD/status u ovom zadatku; paket 2 |
| GitHub `mevan-v2-test` | `be879956ea6ebdc7fc4106459080d3ae85c6202c` | Prethodno potvrđeno spajanje [PR #1](https://github.com/mevan-platform/mevan-diagnostic/pull/1); lokalni remote-tracking ref, bez novog fetch-a |
| Render `mevan-diagnostic-v2-test` | `85fd230eb7d781bb6d25b3e8f1552f8e54f31a2b`, Live; Auto-Deploy Off | Izvorni chat je prijavljeno read-only provjerio dashboard, granu `mevan-v2-test` i [adresu](https://mevan-diagnostic-v2-test.onrender.com); nije nova cloud provjera |

Claude koji samo klonira GitHub **ne dobija paket 2**. Izvori lokalnog commita prenose se patchom na potvrđenu merge osnovu; patch sam ne kreira originalni commit SHA. Nema automatskog deploya iz same predaje; Render postavke se ne mijenjaju.

## Deklarisane i instalirane verzije

`requirements.txt:1` sadrži rasponske zavisnosti, ne lock. Docker koristi python: 3.12-slim bez digest pin-a, CI Python 3.11 i Node 22. Lokalno instalirani interpreter/dependencies ispod su trenutni odabrani venv iz dokumentacijskog pregleda; nisu dokaz Render ili ranijeg CI runtime-a. Nema uv.lock/poetry.lock/requirements.lock/package-lock. Transitivni paketi pydantic/starlette/pillow nisu pojedinačno pinovani.

| Komponenta | Deklaracija / stanje lock-a | Instalirano pri dokumentovanju |
| --- | --- | --- |
| fastapi | >=0.115,<1 | 0.162.3 |
| uvicorn | >=0.30,<1 | 0.54.0 |
| python-docx | >=1.1,<2 | 1.2.0 |
| reportlab | >=4,<5 | 4.5.1 |
| psycopg | [binary]>=3.2,<4 | 3.3.8 |
| psycopg-binary | binary extra psycopg | 3.3.8 |
| pydantic | tranzitivno preko FastAPI | 2.14.3 |
| starlette | tranzitivno preko FastAPI | 1.10.0 |
| pillow | tranzitivno, koristi radar | 13.0.0 |
| httpx | CI/test >=0.27,<1 | 0.28.1 |
| pytest | CI bez verzijskog pina | 9.2.0 |
| playwright | CI bez verzijskog pina | 1.65.0 |
| python | Docker 3.12/CI 3.11 | 3.12.14 (main, Aug 25 2026, 14: 00: 49) [Clang 22.1.3 ] |
| sqlite | stdlib/runtime biblioteka | 3.53.1 |
| node | CI 22 | v24.22.1 |
| chromium | Playwright runner ili lokalni sistemski Chromium | Chromium 156.0.8078.79 built on Debian GNU/Linux 13 (trixie) |
| poppler | OS paket poppler-utils | pdftotext version 25.03.0 |

## Siguran lokalni setup za Claude

Koristiti zaseban direktorij/venv i novu bazu. Ne pokretati komande na stvarnim podacima, produkcijskoj grani ili kroz deploy hook. Sljedeće su upute za lokalni operatorov rad; u ovom dokumentacijskom zadatku nisu izvršeni novi testovi ili deploy.

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install 'httpx>=0.27,<1' pytest playwright
# Debian/Ubuntu, prema ovlaštenju lokalnog operatora:
sudo apt-get install fonts-dejavu-core poppler-utils nodejs
python -m playwright install --with-deps chromium
mkdir -p work
export MEVAN_DB="$PWD/work/mevan-local.sqlite3"
export MEVAN_ADMIN_EMAIL='konsultant@example.invalid'
read -rsp 'Nova lokalna lozinka (najmanje 16 znakova): ' MEVAN_ADMIN_PASSWORD
export MEVAN_ADMIN_PASSWORD
export MEVAN_SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export MEVAN_SECURE_COOKIE=0
export MEVAN_PUBLIC_ORIGIN='http://127.0.0.1:8000'
export MEVAN_ALLOWED_HOSTS='127.0.0.1,localhost'
export MEVAN_ENABLE_HSTS=0
unset OPENAI_API_KEY MEVAN_CANDIDATE_DATABASE_URL
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Server ne učitava automatski .env putem dotenv. Compose env_file to radi za container; u shellu treba export ili operatorov siguran loader. Prazna lozinka/secret iz primjera namjerno neće proći startup. Ne koristiti `source` neprovjerenog env fajla i ne dijeliti stvarne env vrijednosti.

Linux font potreban je na `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`; provjeriti tačnu konstantu FONT u project_reports.py pri drugom OS-u. ReportLab koristi font za bosanske znakove i Pillow radar. Poppler `pdftotext` je potreban testovima izvoza, `pdftoppm` vizuelnom PDF pregledu. python-docx nema Word renderer; instaliranost biblioteke ne potvrđuje paginaciju. Sistemskom Chromiumu u ranijem cloud runneru pristupalo se wrapperom jer Playwright CDN instalacija nije bila dostupna kroz mrežnu politiku; CI koristi standardni playwright install. Ne hardkodirati cloud putanju wrappera u aplikaciju.

## Env ugovor bez tajnih vrijednosti

Siguran primjer je `prenos/config.env.example`; sadrži samo placeholder identitet example.invalid, prazne tajne i lokalne nesenzitivne postavke.

| Varijabla | Default / uslov | Namjena / ograničenje |
| --- | --- | --- |
| MEVAN_DB | SQLite putanja; default BASE/mevan.sqlite3 | Lokalno nova putanja; Compose/data/mevan.sqlite3 |
| MEVAN_ADMIN_EMAIL | Default prazan, obavezan; lowercase/trim | Jedini admin identitet; ne kopirati stvarnu adresu |
| MEVAN_ADMIN_PASSWORD | Default prazna; startup>=12, preflight>=16 | Tajna; nema vrijednosti u predaji |
| MEVAN_SESSION_SECRET | Default prazan; najmanje 32 | Tajna za HMAC; bez stvarne vrijednosti |
| MEVAN_SECURE_COOKIE | Default 1 | 0 samo lokalni HTTP |
| MEVAN_PUBLIC_ORIGIN | Default prazan→req.base_url | Za hosting eksplicitni HTTPS origin bez završnog slash-a |
| MEVAN_ALLOWED_HOSTS | Default prazan→allowlist kontrola nije aktivna | CSV hostova; ne zamijeniti tenant kontrolom |
| MEVAN_ENABLE_HSTS | Default 0 | 1 samo uz pravilni HTTPS hosting |
| OPENAI_API_KEY | Default prazan→AI503 | Optional tajna, samo server |
| MEVAN_AI_MODEL | Default gpt-4.1-mini | Optional model za sve postojeće OpenAI puteve |
| MEVAN_CANDIDATE_DATABASE_URL | Default prazan→SQLite nacrti | Optional tajni PG URL; samo kandidati, bez auto-DDL |
| MEVAN_QA_ARTIFACT_DIR | Optional browser QA izlaz | Samo sintetički screenshoti/izvozi |
| MEVAN_WORD_QA_DIR | Default qa_docx u repo kod QA skripte | Uvijek dati novu vanjsku putanju da se stari rezultati ne prepišu |

## Tačne komande provjera

```bash
# Iz korijena prenesenog source checkouta i aktivnog venv-a:
python -m pytest -q --junitxml=work/pytest-novi.xml
MEVAN_WORD_QA_DIR="$PWD/work/word-novi" node qa_word_reports.js
MEVAN_WORD_QA_DIR="$PWD/work/word-novi" python qa_word_reports.py
python http_release_smoke.py
python release_preflight.py
# --runtime je provjera HTTPS konfiguracije; lokalni HTTP primjer namjerno je ne prolazi.
```

`pytest` na ovoj verziji uključuje 168 slučajeva prema sačuvanom logu. To nije garancija identičnih budućih instalacija bez lock-a. Mnoge testne metode same podešavaju temp DB/env; browser skripte zahtijevaju već pokrenut izolovani server 8382 i sintetičku QA prijavu usklađenu sa skriptom. Ne pokretati browser_approved_smoke.py ili browser_package 2.py protiv stvarnog hostinga: one namjerno mijenjaju sintetički workspace/projekte.

Za browser pripremiti zaseban privremeni proces, izvorno pogledati `.github/workflows/mevan-sync-test.yml:44` i obje browser skripte. CI koristi njihove fiksne sintetičke test vrijednosti; one nisu deployment tajne i ne prepisuju se u ovaj operaterski primjer. `MEVAN_PUBLIC_ORIGIN` mora odgovarati 8382 ili biti prazna za same-origin test. Pri završetku zaustaviti proces i ukloniti samo vlastiti temp direktorij. Novi screenshot/PDF izlazi idu izvan repozitorija. U ovom dokumentacijskom zadatku nije potrebno ponavljati već uspješne provjere.

## CI ugovor i ograničenja

`.github/workflows/mevan-sync-test.yml:1`:

- push samo na staru test granu `mevan-test-sync-bk-qg-20261110`;
- pull_request prema `mevan-v2-test` (bez path filtera; podrazumijevani PR tipovi događaja);
- workflow_dispatch ručno, bez automatskog poziva u ovom zadatku;
- contents:read, checkout persist-credentials:false, bez secrets, bez deploy joba/pull_request_target;
- ubuntu-latest, timeout 20 min; Python 3.11, Node 22, DejaVu/Poppler, requirements+httpx/pytest/playwright;
- compile odabranih TEST modula, cijeli pytest, svih 12 Word QA, playwright Chromium i **browser_approved_smoke.py**.

Paket 2 novu browser_package 2.py **nije dodao u workflow**. Ako se kod naknadno odobreno prenese u PR, pytest bi pokupio nove testove, ali cijeli novi Guided browser tok neće automatski biti poseban CI korak bez buduće izmjene. Trenutni lokalni paket 2 nije pushan, zato nema novog CI runa za njega. Prvi CI136/Word 12/Chromium uspjeh vezan je uz prethodni head, ne novi `132ef28`. CI ne testira stvarni AI, Render dashboard ili udaljeni PG; OPENAI_API_KEY i candidate URL namjerno su prazni.

## Docker i hosting materijal

Dockerfile instalira fonts-dejavu-core i requirements, kreira ne-root korisnika mevan, kopira server/index/engine/gate, mevan_*.py/approved_reports/diagnostic_review i project_*.py/projects_ui/dashboard. V2 report model je obuhvaćen postojećim wildcardom. Ne kopira svaki CLI/test: backup_restore.py i QA skripte nisu automatski dostupne u imageu. EXPOSE8000, uvicorn 0.0.0.0: 8000 uz proxy headers i forwarded-allow-ips 127.0.0.1. Treba posebno potvrditi hosting PORT i proxy ponašanje prije odobrenog deploya; Dockerfile nije dokaz Render aktivne konfiguracije.

Compose bind 127.0.0.1: 8000, volume mevan_data:/data, read_only, tmpfs/tmp, no-new-privileges, restart unless-stopped. To je lokalni Docker predložak, ne read-only potvrda žive postavke. Nema render.yaml blueprinta u praćenim datotekama; dashboard stanje je preneseni dokaz izvornog chata. Nema deploy hooka u ovoj predaji i nijedan deploy nije pozvan.

## Backup postupak i preduslovi

Offline CLI primjeri (putanje su isključivo sintetičke):

```bash
python backup_restore.py verify work/mevan-local.sqlite3
python backup_restore.py backup work/mevan-local.sqlite3 work/kopije/nova-kopija.sqlite3
python backup_restore.py restore work/kopije/nova-kopija.sqlite3 work/vraceno-nova-putanja.sqlite3
```

Odredište mora biti novo; ne prepisuje postojeće. backup koristi sqlite3 backup API uključujući WAL; verify integrity_check. Prije stvarnog prebacivanja DB putanje zaustaviti aplikaciju, sačuvati predhodno stanje, provjeriti dozvole i imati odobren operaterski plan. Šifrovanje, offsite pohrana i raspored nisu implementirani. Zaseban PG i vanjske datoteke nisu pokriveni; JSON backup ima uži obuhvat. [Arhitektura](DATABASE_AND_ARCHITECTURE.md) daje tačnu matricu obuhvata.

## Prenos lokalnog commita

Tačne patch komande i provjera izvornog stabla su u [Claude handoveru](CLAUDE_MASTER_HANDOVER.md). Ne treba push da bi korisnik prenio lokalni commit; patch zahtijeva potvrđenu merge osnovu. Bundle je lokalno provjeren, ali nije u ZIP-u jer zadržava identitet autora. Source archive nema Git historiju i izostavlja .env.example zbog privatnog identiteta. To nije nova aplikacija ili migracija klijentskih podataka.
