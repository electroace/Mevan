> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: svi registrovani endpointi, ulazni/izlazni ugovori i funkcionalni tokovi.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — funkcionalna specifikacija

## Sistemske granice i tokovi

Pristup je jedinstvena administratorska sesija, bez javne registracije ili razdvojenih uloga. Glavni ekran `/` ima lokalni/legacy JSON workspace; `/diagnostic-review` je odvojeni revizionisani pregled s novim zaključanim izvještajima; `/projects-ui` upravlja postojećim projektnim objektima; `/dashboard-ui` daje read-only portfolio. Login i health su javni. OpenAPI/dokumentacijski URL-ovi su isključeni u app konstruktoru, iako je šema programatski izvučena u ovom paketu.

Stari tok: profil → modul/kriterij → lokalna pravila/AI nacrt → interno simulacijsko odobrenje → browser print ili ručni OOXML Word. Novi tok: odabrana dijagnostika → Guided intervju/dokumenti/obilazak/dokazi → sažetak/prioriteti/projekat/plan → provjera 61 kriterija i revizije → nepromjenjiv snimak → oba prikaza PDF/DOCX. Paralelni put v3 pravi strukturirani AI nacrt i dva radna Word prikaza; to nije finalni gate. Projektni put: kandidati → pet faktora → rangiranje → deterministički/AI nacrt → draft → validation/implementation → sedmični pregledi i efekti → projektni izvještaj. Putanje se ne smiju ukloniti samo zato što je novi tok pregledniji.

## Zajednički ugovori

API radi JSON-om osim login URL-encoded forme i binarnih izvoza. Pydantic tijelo u pravilu daje 422 za neispravan tip/obavezno polje. Ručno parsirani Request handleri koriste vlastite 400/413. GET zahtjevi nisu svuda potpuno bez nuspojava: lazy CREATE inicijalizuje šemu, a `/api/backup` upisuje audit događaj. Nema obećane globalne transakcije preko SQLite+opcionalnog PG. Neprijavljen API401; mutirajući zaštićeni zahtjev bez matching Origin/Referer 403; login ima vlastiti potpisani token. Status greške nije dovoljan za tvrdnju o stručnoj validnosti.

`/api/workspace` očekuje workspace kao korijenski objekt, a ne `{workspace:...}`. `If-Match` je hash prethodnog sirovog JSON stringa; početno `'empty'`. `/api/test/v2/workspace` očekuje `{workspace:...,expected_revision:int}`; početna revizija 0; konflikt 409 vraća current_revision. Kandidat nacrt također ima expected_revision, ali drugi ugovor/šemu. Ne miješati tri mehanizma.

Veličine: workspace/restore 4MiB; quality check 1MiB; deterministic analyze 250000 bajtova; basic AI55000; integrated/decisions/v 3150000; kandidat nacrt model_dump_json 1 milion znakova. Projektne dict/list unutrašnjosti nemaju univerzalni HTTP body limit u svim rutama, što je ograničenje.

## Ulazne JSON strukture i izlazne porodice

Workspace: `{schema:3,companies:[{id,company:{name,industry,employees,revenue,location,erp,contact},diagnostics:[{id,name,date,assess,plan,approved,review,effects,v2,v3,quality_records,risk_reviews,consultant_review,guided,report_mode}]}],activeCompanyId,activeDiagnosticId}`. Stvarna polja se razvijaju paralelno; nije normalizovana Pydantic šema cijelog workspacea. Nedostajuća/extra polja nisu svugdje strogo odbijena. `assess[code]` sadrži score/proof/applicable/evidence/finding/kpi/financial/recommendation i po potrebi na_reason/na_approved_by/is_simulated. `quality_records` i consultant_review su opisani u [poslovnoj logici](BUSINESS_LOGIC.md).

Analysis rezultati: deterministic `{version,label,index,index_status,dimensions,coverage,critical,causal_hypotheses,priority_decisions,weak_criteria,finance,limitations}`; v3 `{version,approved:false,source,company,criteria,facts,analysis,limitations,report_views,quality_gate}`. AI nije autoritet za facts. Kandidati vraćaju neodobreni status i candidates; ranking vraća score/rank/unverified_factors/weights; draft vraća charter i obavezno ljudsko odobrenje. Projekat vraća identitet/status/charter/weeklies; finansije vraćaju procjenu; actual-effect 201 vraća id/status/replayed i false za nezavisnu verifikaciju.

Svi registrovani endpointi navedeni su ispod, jedan po metodi. Za ručno parsirano tijelo OpenAPI može nemati requestBody; to znači da ga handler parsira sam, ne da je tijelo nepotrebno. Izrazi return/raise preuzeti su iz AST-a kao precizan tehnički dokaz; neki složeni izrazi su Python notacija, a ne primjer JSON teksta. `raise ValueError` koji nije uhvaćen na granici handlera može biti 500, ne automatski 422. Ugovori o error statusima slijede stvarni kod, ne idealizovanu specifikaciju.

### API-01 — `GET /login`

**Svrha/obrada:** Prikazuje formu s potpisanim 15-minutnim tokenom; ne izdaje sesiju.

**Pristup i zaštita:** javno; GET bez provjere porijekla. Handler `login_page`, izvor `server.py:97`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `'<!doctype html><html lang="bs"><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><title>MEVAN – prijava</title><style>body{font:16px system-ui;background:#f3f6fa;color:#193047;display:grid;place-items:center;min-height:90vh}form{background:white;padding:32px;border-radius:16px;max-width:370px;width:90%;box-shadow:0 8px 28px #142e4618}input,button{box-sizing:border-box;width:100%;padding:13px;margin:9px 0;border-radius:9px;border:1px solid #ccd6df}button{background:#0a6485;color:white;border:0;font-weight:700}</style><form method="post" action="/login"><input type="hidden" name="csrf_token" value="__CSRF_TOKEN__"><h1>MEVAN Diagnostic</h1><p>Privatni demonstracijski pristup</p><label>E-mail<input name="email" type="email" required autocomplete="username"></label><label>Lozinka<input name="password" type="password" required autocomplete="current-password"></label><button>Prijavi se</button></form></html>'.replace('__CSRF_TOKEN__', login_csrf_token())`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-02 — `POST /login`

**Svrha/obrada:** Provjerava token, IP limit, e-mail/lozinku; postavlja 8 h kolačić i bilježi audit; uspjeh 303.

**Pristup i zaštita:** javno; potpisani prijavni CSRF token. Handler `login`, izvor `server.py:101`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `resp`
- `HTMLResponse('Pogrešna prijava. <a href="/login">Pokušaj ponovo</a>.', status_code=401)`

**Validacije i eksplicitne greške:**

- `raise HTTPException(403, 'Nevažeći sigurnosni token. Osvježite stranicu za prijavu.')`
- `raise HTTPException(429, 'Previše pokušaja. Pokušajte kasnije.')`


### API-03 — `POST /logout`

**Svrha/obrada:** Briše sesijski kolačić, po potrebi audit; 303 na login.

**Pristup i zaštita:** valjana sesija nije obavezna za brisanje kolačića; audit odjave upisuje se samo za prijavljenog administratora; Origin/Referer. Handler `logout`, izvor `server.py:126`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `resp`

**Validacije i eksplicitne greške:**

- `raise HTTPException(403, 'Nedozvoljen izvor')`


### API-04 — `GET /`

**Svrha/obrada:** Vraća glavni HTML prijavljenom korisniku; inače 307 redirect.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `home`, izvor `server.py:133`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `HTMLResponse(html, headers={'Cache-Control': 'no-store', 'Content-Security-Policy': "frame-ancestors 'none'", 'X-Content-Type-Options': 'nosniff'})`
- `RedirectResponse('/login')`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-05 — `GET /api/workspace`

**Svrha/obrada:** Čita legacy JSON workspace i verziju SHA256; bez reda workspace=null, version=empty.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `load`, izvor `server.py:139`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'workspace': json.loads(row[0]) if row else None, 'updated': row[1] if row else None, 'version': hashlib.sha256(row[0].encode()).hexdigest() if row else 'empty'}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`


### API-06 — `PUT /api/workspace`

**Svrha/obrada:** CAS zapis legacy radnog prostora uz audit u istoj SQLite transakciji.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `store`, izvor `server.py:147`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'ok': True, 'version': hashlib.sha256(encoded.encode()).hexdigest()}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(413, 'Prevelika dijagnostika')`
- `raise HTTPException(400, 'Neispravan radni prostor')`
- `raise HTTPException(400, 'Neispravan JSON')`
- `raise HTTPException(400, 'Neispravan zapis kompanije')`
- `raise HTTPException(409, 'Radni prostor je promijenjen. Uporedite lokalnu i serversku verziju.')`


### API-07 — `POST /api/v2/data-quality/check`

**Svrha/obrada:** Read-only tehnička kontrola liste records; ne čuva niti potvrđuje dokaz.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `data_quality_check`, izvor `server.py:173`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `check_batch(payload.get('records'))`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(413, 'Prevelik zahtjev')`
- `raise HTTPException(400, str(exc))`


### API-08 — `GET /api/backup`

**Svrha/obrada:** Izvozi samo legacy workspace u mevan-backup-v1; ne cijelu bazu.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `backup`, izvor `server.py:187`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `Response(json.dumps(data, ensure_ascii=False), media_type='application/json', headers={'Content-Disposition': 'attachment; filename="mevan-sigurnosna-kopija.json"', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(404, 'Nema podataka za sigurnosnu kopiju')`


### API-09 — `GET /api/audit`

**Svrha/obrada:** Vraća posljednjih 100 legacy audit događaja.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `audit`, izvor `server.py:198`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'events': [{'timestamp': r[0], 'event': r[1], 'details': r[2]} for r in rows]}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`


### API-10 — `POST /api/backup/restore`

**Svrha/obrada:** Ručno prepisuje samo legacy workspace nakon X-Mevan-Confirm-Restore=VRATI-PODATKE; nema automatskog mergea.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `restore`, izvor `server.py:204`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'ok': True}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(400, 'Potrebna izričita potvrda vraćanja')`
- `raise HTTPException(413)`
- `raise HTTPException(400, 'Neispravan format sigurnosne kopije')`
- `raise HTTPException(400, 'Neispravan radni prostor')`
- `raise HTTPException(400, 'Neispravan JSON')`
- `raise HTTPException(400, 'Neispravna kompanija')`


### API-11 — `POST /api/v2/analyze`

**Svrha/obrada:** Lokalni deterministički analyze bez vanjskog poziva.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `diagnostic_v2`, izvor `server.py:224`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `analyze(data)`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(413, 'Prevelik zahtjev')`
- `raise ValueError()`
- `raise HTTPException(400, 'Neispravan ulaz za MEVAN v2')`


### API-12 — `GET /health`

**Svrha/obrada:** Javni liveness odgovor status=ok; ne provjerava DB/AI.

**Pristup i zaštita:** javno; GET bez provjere porijekla. Handler `health`, izvor `server.py:237`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'status': 'ok'}`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-13 — `POST /api/ai/draft`

**Svrha/obrada:** Jednomodulski/ALL generativni tekst nacrta; bez ključa 503; timeout 35 s, max_tokens 1200.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `ai_draft`, izvor `server.py:241`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'draft': draft, 'source': 'generative_ai', 'approved': False}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(503, 'AI servis nije konfigurisan. Lokalna analiza po pravilima je dostupna.')`
- `raise HTTPException(413, 'Prevelik zahtjev')`
- `raise HTTPException(400, 'Neispravna dimenzija')`
- `raise HTTPException(400, 'Neispravni kriteriji')`
- `raise HTTPException(400, 'Neispravan zahtjev')`
- `raise HTTPException(400)`
- `raise HTTPException(502, 'AI servis trenutno nije dostupan; pokušajte kasnije.')`


### API-14 — `POST /api/v2/ai-integrated`

**Svrha/obrada:** Integrisani tekst nacrta uz lokalne rule činjenice; timeout 85 s, max_tokens 3300; bez odobrenja.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `ai_integrated`, izvor `server.py:311`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'draft': draft, 'approved': False, 'source': 'generative_ai', 'rules_version': result.get('version')}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(503, 'AI servis nije konfigurisan.')`
- `raise HTTPException(413, 'Prevelik zahtjev')`
- `raise ValueError()`
- `raise HTTPException(400, 'Neispravan ulaz')`
- `raise ValueError()`
- `raise HTTPException(502, 'AI servis odbio zahtjev (HTTP ' + str(e.code) + '). Provjerite model, budžet i pristup.')`
- `raise HTTPException(502, 'AI servis nije vratio ispravan odgovor. Pokušajte ponovo.')`


### API-15 — `POST /api/v2/decisions`

**Svrha/obrada:** Direktorske preporuke tekstom; timeout 85 s, max_tokens 3900; ne persistira approved nalaz.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `decision_intelligence`, izvor `server.py:382`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'draft': draft, 'approved': False, 'source': 'generative_ai', 'rules_version': rules.get('version')}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(503, 'AI servis nije konfigurisan.')`
- `raise HTTPException(413, 'Prevelik zahtjev')`
- `raise ValueError()`
- `raise HTTPException(400, 'Neispravan ulaz')`
- `raise ValueError()`
- `raise HTTPException(502, 'AI servis odbio zahtjev (HTTP ' + str(e.code) + ').')`
- `raise HTTPException(502, 'AI servis nije vratio ispravan odgovor.')`


### API-16 — `POST /api/v3/analyze`

**Svrha/obrada:** Strukturirani AI JSON uz kanonske facts; timeout 85 s, max_tokens 4200; neprihvatljiv odgovor 502.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `mevan_v3_analyze`, izvor `server.py:447`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'version': '3.4-decision-gates', 'approved': False, 'source': 'rules_plus_ai', 'company': company, 'criteria': criteria, 'facts': {'index': rules['index'], 'dimensions': rules['dimensions'], 'coverage': rules['coverage'], 'critical': rules['critical'], 'finance': rules['finance']}, 'analysis': draft, 'limitations': rules['limitations'], 'report_views': {'short': 'executive_summary + top decisions + selected KPI + canonical facts', 'long': 'same analysis + all criteria + full evidence and finance register'}, 'quality_gate': {'independent_verification': False, 'consultant_approved': False, 'finance_recalculated_by_ai': False}}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(401)`
- `raise HTTPException(403)`
- `raise HTTPException(413, 'Prevelik zahtjev')`
- `raise HTTPException(503, 'AI servis nije konfigurisan.')`
- `raise ValueError()`
- `raise ValueError()`
- `raise HTTPException(400, 'Neispravan ulaz')`
- `raise ValueError('Neispravan AI format')`
- `raise ValueError('Nepotpuna AI analiza')`
- `raise ValueError('Sažetak')`
- `raise ValueError('Plan')`
- `raise HTTPException(502, 'AI servis odbio zahtjev (HTTP ' + str(e.code) + ').')`
- `raise HTTPException(502, 'AI nije vratio ispravan strukturirani nacrt; ništa nije odobreno.')`
- `raise ValueError(field)`
- `raise ValueError('Neispravan KPI')`
- `raise ValueError('Nepotpuna KPI definicija')`
- `raise ValueError('Odluka bez validnog KPI')`
- `raise ValueError('Odluka bez uslova')`
- `raise ValueError('Nedostaje konkurentska hipoteza')`
- `raise ValueError('Neispravan period plana')`
- `raise ValueError(field)`
- `raise ValueError('Nepoznata šifra kriterija')`
- `raise ValueError('Neispravna aktivnost')`


### API-17 — `GET /projects-ui`

**Svrha/obrada:** Zaštićena postojeća projektna HTML stranica, neprijavljen 303.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `project_ui`, izvor `server.py:604`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `HTMLResponse((Path(__file__).parent / 'projects_ui.html').read_text(encoding='utf-8'))`
- `RedirectResponse('/login', status_code=303)`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-18 — `GET /dashboard-ui`

**Svrha/obrada:** Zaštićena portfolio HTML stranica, neprijavljen 303.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `dashboard_ui`, izvor `server.py:611`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `HTMLResponse((Path(__file__).parent / 'dashboard_ui.html').read_text(encoding='utf-8'))`
- `RedirectResponse('/login', status_code=303)`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-19 — `GET /diagnostic-review`

**Svrha/obrada:** Zaštićeni Guided/gate ekran; neprijavljen 303; odabir dijagnostike prenosi sessionStorage.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `diagnostic_review`, izvor `server.py:621`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `HTMLResponse((BASE / 'diagnostic_review.html').read_text(encoding='utf-8'))`
- `RedirectResponse('/login', status_code=303)`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-20 — `POST /api/v4/projects`

**Svrha/obrada:** Stvara UUID draft i audit; odbija drugi aktivni projekat iste dijagnostike.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `create_project`, izvor `project_execution.py:98`. Deklarisani status 201; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ProjectIn"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `{'id': pid, 'status': 'draft'}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(409, 'Dijagnostika već ima aktivan projektni nacrt')`


### API-21 — `GET /api/v4/projects/{pid}/audit`

**Svrha/obrada:** Čita audit po projektu u redoslijedu created_at, rowid.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `project_audit`, izvor `project_execution.py:112`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'events': [dict(r) for r in rows]}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404, 'Projekat nije pronađen')`


### API-22 — `GET /api/v4/projects`

**Svrha/obrada:** Lista sve projekte instance, bez tenant filtera.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `list_projects`, izvor `project_execution.py:122`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'projects': [dict(r) for r in rows]}`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-23 — `GET /api/v4/projects/{pid}`

**Svrha/obrada:** Detalj projekta i sedmični pregledi; ne uključuje automatski sve finansije/efekte.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `get_project`, izvor `project_execution.py:129`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `data`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404)`


### API-24 — `PUT /api/v4/projects/{pid}/charter`

**Svrha/obrada:** Uređuje charter samo draft/validation, uz audit stvarne razlike i nepromjenjiv režim.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `edit_project`, izvor `project_execution.py:139`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo (OpenAPI ugovor):**

```json
{
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/Charter"
      }
    }
  }
}
```

**Izlazi u kodu:**

- `{'ok': True}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404)`
- `raise HTTPException(409, 'Odobren projekat se ne mijenja bez nove verzije')`
- `raise HTTPException(409, 'Način postojećeg projekta se ne može preimenovati; DEMO ostaje simulacija')`


### API-25 — `POST /api/v4/projects/{pid}/approve-validation`

**Svrha/obrada:** Dozvoljava samo draft→validation i bilježi audit.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `approve_validation`, izvor `project_execution.py:155`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'status': 'validation'}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404)`
- `raise HTTPException(409, 'Neispravan prijelaz statusa')`


### API-26 — `POST /api/v4/projects/{pid}/approve-implementation`

**Svrha/obrada:** Dozvoljava draft/validation→implementation uz tri potvrde; DEMO odbija.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `approve_implementation`, izvor `project_execution.py:168`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo:** Ručno parsirano u Request handleru; format/limit opisan gore i u izrazu validacije ispod.

**Izlazi u kodu:**

- `{'status': 'implementation'}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404)`
- `raise HTTPException(409, 'Neispravan prijelaz statusa')`
- `raise HTTPException(409, 'DEMO — simulirani podaci: nije dozvoljeno stvarno odobrenje implementacije')`
- `raise HTTPException(409, 'Prvo potvrditi početno stanje, ciljeve i obavezne provjere')`


### API-27 — `POST /api/v4/projects/{pid}/weekly-reviews`

**Svrha/obrada:** Dodaje jedinstven sedmični pregled samo tokom implementacije, uz audit.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `add_review`, izvor `project_execution.py:186`. Deklarisani status 201; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo (OpenAPI ugovor):**

```json
{
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ReviewIn"
      }
    }
  }
}
```

**Izlazi u kodu:**

- `{'ok': True, 'week': payload.week}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404)`
- `raise HTTPException(409, 'Sedmični pregled dozvoljen samo u implementaciji')`
- `raise HTTPException(409, 'Sedmični pregled već postoji')`


### API-28 — `GET /api/v4/candidate-drafts`

**Svrha/obrada:** Čita company_id/diagnostic_id nacrt iz lokalnog SQLite ili opcionalnog PG; 404 nema nacrta.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `get_candidate_draft`, izvor `project_execution.py:218`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `company_id` (query, obavezan): `{"type": "string", "title": "Company Id"}`; `diagnostic_id` (query, obavezan): `{"type": "string", "title": "Diagnostic Id"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'draft': row[0] if isinstance(row[0], dict) else json.loads(row[0]), 'revision': row[1], 'updated_at': row[2]}`
- `{'draft': json.loads(row[0]), 'revision': row[1], 'updated_at': row[2]}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, 'Neispravni identifikatori')`
- `raise HTTPException(404, 'Serverski nacrt nije pronađen')`
- `raise HTTPException(404, 'Serverski nacrt nije pronađen')`


### API-29 — `PUT /api/v4/candidate-drafts`

**Svrha/obrada:** Validira ocjene, računa rangiranje i čuva CAS reviziju; PG zahtijeva već pripremljenu tabelu.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `put_candidate_draft`, izvor `project_execution.py:235`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CandidateDraftIn"
      }
    }
  }
}
```

**Izlazi u kodu:**

- `{'saved': True, 'revision': row[0], 'updated_at': now, 'ranking': data['ranking']}`
- `{'saved': True, 'revision': payload.expected_revision + 1, 'updated_at': now, 'ranking': data['ranking']}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(413, 'Nacrt je prevelik')`
- `raise HTTPException(422, 'Nepostojeći kandidat u ocjenama')`
- `raise HTTPException(422, 'Neispravni faktori')`
- `raise HTTPException(409, 'Serverski nacrt je promijenjen. Učitajte ga i uporedite prije ponovnog čuvanja.')`
- `raise HTTPException(422, 'Neispravan zapis ocjene')`
- `raise HTTPException(422, 'Ocjena mora biti 0–5')`
- `raise HTTPException(422, 'Tekst ocjene je predug')`
- `raise HTTPException(409, 'Serverski nacrt je promijenjen. Ponovo učitajte ocjene.')`


### API-30 — `POST /api/v4/project-candidates`

**Svrha/obrada:** Pretvara neodobrenu analizu u kandidatske odluke; nema čuvanja ili verifikacije.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `project_candidates`, izvor `project_execution.py:293`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "additionalProperties": true,
        "type": "object",
        "title": "Payload"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `prepare_candidates(analysis)`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, 'Nedostaje analiza')`


### API-31 — `POST /api/v4/rank-projects`

**Svrha/obrada:** Validira pet faktora i rangira; ne odobrava niti upisuje projekat.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `rank_projects`, izvor `project_execution.py:303`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "additionalProperties": true,
        "type": "object",
        "title": "Payload"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `rank(p.analysis, p.ratings)`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, str(e))`


### API-32 — `POST /api/v4/project-draft`

**Svrha/obrada:** Pravi deterministički validacijski charter, bez baseline/ciljeva/koristi.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `generate_project_draft`, izvor `project_execution.py:313`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "additionalProperties": true,
        "type": "object",
        "title": "Payload"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `draft(DraftRequest.model_validate(payload))`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, str(e))`


### API-33 — `POST /api/v4/project-ai-pack`

**Svrha/obrada:** Pravi AIPlan kroz strogu Pydantic šemu; nema upisa ili aktiviranja projekta; timeout 60 s, max_tokens 4500.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `project_ai_pack`, izvor `project_execution.py:322`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "additionalProperties": true,
        "type": "object",
        "title": "Payload"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `generate(DraftRequest.model_validate(payload))`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, 'AI projektni nacrt nije validan: ' + str(e)[:200])`
- `raise HTTPException(503, str(e))`
- `raise HTTPException(502, 'AI servis trenutno nije dostupan ili odgovor nije ispravan')`


### API-34 — `POST /api/v4/financial-scenarios/calculate`

**Svrha/obrada:** Stateless finansijski kalkulator samo estimated scenarija.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `calculate_financial_scenarios`, izvor `project_execution.py:338`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "additionalProperties": true,
        "type": "object",
        "title": "Payload"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `calculate(FinancialModel.model_validate(payload))`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-35 — `GET /api/v4/projects/{pid}/financial-model`

**Svrha/obrada:** Čita sačuvani model i ponovo računa procjenu; ako nema modela, tri izlazna polja=null.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `get_project_financial_model`, izvor `project_execution.py:346`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'model': model.model_dump(mode='json'), 'calculation': calculate(model), 'updated_at': saved['updated_at']}`
- `{'model': None, 'calculation': None, 'updated_at': None}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404, 'Projekat nije pronađen')`


### API-36 — `PUT /api/v4/projects/{pid}/financial-model`

**Svrha/obrada:** Čuva finansijski JSON samo draft/validation; stvarna promjena i audit su isti commit.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `save_project_financial_model`, izvor `project_execution.py:358`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo (OpenAPI ugovor):**

```json
{
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "type": "object",
        "additionalProperties": true,
        "title": "Payload"
      }
    }
  }
}
```

**Izlazi u kodu:**

- `{'saved': True, 'calculation': calculate(model)}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404, 'Projekat nije pronađen')`
- `raise HTTPException(409, 'Finansijski scenariji odobrenog projekta su zaključani')`


### API-37 — `GET /api/v4/projects/{pid}/actual-effects`

**Svrha/obrada:** Čita efekte i sumira potvrđene konsultantske iznose odvojeno od obrtnog kapitala.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `get_actual_effects`, izvor `project_execution.py:379`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'entries': entries, 'summary': summarize(entries)}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404)`


### API-38 — `POST /api/v4/projects/{pid}/actual-effects`

**Svrha/obrada:** Idempotentni upis efekta tokom implementation; retry 201 sa istim ID/replayed=true; isti event/drugi sadržaj 409.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `add_actual_effect`, izvor `project_execution.py:389`. Deklarisani status 201; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`

**Tijelo (OpenAPI ugovor):**

```json
{
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "type": "object",
        "additionalProperties": true,
        "title": "Payload"
      }
    }
  }
}
```

**Izlazi u kodu:**

- `{'id': eid, 'status': 'consultant_confirmed' if effect.consultant_confirmed else 'pending', 'independently_verified': False, 'replayed': False}`
- `{'id': eid, 'status': 'consultant_confirmed' if effect.consultant_confirmed else 'pending', 'independently_verified': False, 'replayed': True}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, 'Oznaka događaja mora imati 1–128 slova bez dijakritike, cifara ili znakova . _ : -')`
- `raise HTTPException(422, 'Provjerite period, iznos, dokaz, obračun i vlasnika finansijskog efekta.') from exc`
- `raise HTTPException(404)`
- `raise HTTPException(409, 'Efekti se evidentiraju samo tokom implementacije')`
- `raise HTTPException(409, 'Oznaka događaja je već korištena za drugi sadržaj. Ponovite izvorni zahtjev ili koristite novu oznaku za zaseban događaj.')`


### API-39 — `GET /api/v4/projects/{pid}/report/{fmt}`

**Svrha/obrada:** Read-only snapshot projekta u jednoj SQLite read transakciji; projektni PDF/DOCX, nepodržan format 404.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `project_report`, izvor `project_execution.py:424`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `pid` (path, obavezan): `{"type": "string", "title": "Pid"}`; `fmt` (path, obavezan): `{"type": "string", "title": "Fmt"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `Response(content, media_type=media, headers={'Content-Disposition': f'attachment; filename="MEVAN_project_{pid[:8]}.{fmt}"', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})`

**Validacije i eksplicitne greške:**

- `raise HTTPException(404, 'Nepodržan format')`
- `raise HTTPException(404, 'Projekat nije pronađen')`


### API-40 — `GET /api/v4/dashboard`

**Svrha/obrada:** Read-only portfolio svih projekata; broji potencijalno zakašnjele datume, bez finansijskog sabiranja perioda.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `project_dashboard`, izvor `project_execution.py:444`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{'projects': projects, 'summary': {'companies': len({p['company_id'] for p in projects}), 'projects': len(projects), 'by_status': statuses, 'projects_with_overdue_activities': sum((bool(p['overdue_activities']) for p in projects)), 'projects_with_financial_model': sum((p['financial_model_present'] for p in projects))}, 'disclaimer': 'Rokovi su iz projektnog nacrta i ne uzimaju u obzir završetak aktivnosti. Iznosi različitih perioda nisu sabrani. Konsultantski potvrđeni efekti nisu nezavisno verificirani.'}`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-41 — `GET /api/test/v2/workspace`

**Svrha/obrada:** Čita odvojeni revizionisani TEST workspace i reviewer_id iz konfiguracije.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `get_test_workspace`, izvor `mevan_test_workspace_api.py:54`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `{**read_test_workspace(db), 'reviewer_id': reviewer_id}`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-42 — `PUT /api/test/v2/workspace`

**Svrha/obrada:** Čuva TEST workspace u BEGIN IMMEDIATE uz očekivanu reviziju; izolovane tabele, ista DB putanja instance.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `put_test_workspace`, izvor `mevan_test_workspace_api.py:60`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/SaveRequest"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `{'ok': True, 'revision': revision}`

**Validacije i eksplicitne greške:**

- `raise HTTPException(403, 'Neispravno porijeklo zahtjeva')`
- `raise HTTPException(status_code=409, detail={'code': 'REVISION_CONFLICT', 'current_revision': current['revision']})`
- `raise HTTPException(status_code=422, detail=str(exc))`


### API-43 — `POST /api/test/v2/approvals`

**Svrha/obrada:** Prethodno tehnički validira sedam review polja, zatim gate+snimak atomarno; reviewer ne dolazi iz klijentskog tijela.

**Pristup i zaštita:** sesija jednog administratora; Origin/Referer. Handler `approve`, izvor `mevan_test_workspace_api.py:83`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo (OpenAPI ugovor):**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ApprovalRequest"
      }
    }
  },
  "required": true
}
```

**Izlazi u kodu:**

- `approve_workspace(db, body.expected_revision, reviewer_id, body.company_index, body.diagnostic_index)`

**Validacije i eksplicitne greške:**

- `raise HTTPException(403, 'Neispravno porijeklo zahtjeva')`
- `raise RevisionConflict('Radni prostor je promijenjen')`
- `raise HTTPException(409, str(exc)) from exc`
- `raise HTTPException(422, str(exc)) from exc`
- `raise ApprovalError('Nepoznata dijagnostika') from exc`


### API-44 — `GET /api/test/v2/approvals`

**Svrha/obrada:** Lista historijske bound-v1 i bound-v2 snimke s režimom; nije dokaz da su stvarni podaci provjereni.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `approvals`, izvor `mevan_test_workspace_api.py:107`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** Nema deklarisanih path/query parametara; eventualna ručna zaglavlja i tijelo su u opisu handlera.

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `[dict(approval_id=id_, revision=rev, reviewer=who, diagnostic_id=diag, report_mode=mode) for id_, rev, who, diag, mode in rows]`

**Validacije i eksplicitne greške:**

- Nema lokalnog raise; zajednička autentikacija/origin ili framework i I/O greške mogu prekinuti zahtjev.


### API-45 — `GET /api/test/v2/approvals/{approval_id}/{view}/{fmt}`

**Svrha/obrada:** Isti zaključani izvor za executive/detailed × pdf/docx; režim se čita iz snimka, ne iz query parametra.

**Pristup i zaštita:** sesija jednog administratora; GET bez provjere porijekla. Handler `download`, izvor `mevan_test_workspace_api.py:115`. Deklarisani status 200; RedirectResponse/Response može eksplicitno promijeniti status.

**Parametri:** `approval_id` (path, obavezan): `{"type": "integer", "title": "Approval Id"}`; `view` (path, obavezan): `{"enum": ["executive", "detailed"], "type": "string", "title": "View"}`; `fmt` (path, obavezan): `{"enum": ["pdf", "docx"], "type": "string", "title": "Fmt"}`

**Tijelo:** Nije deklarisano.

**Izlazi u kodu:**

- `Response(content, media_type=mime, headers={'Content-Disposition': f'''attachment; filename="MEVAN_{approval_id}_{('DEMO_' if mode == 'demo' else '')}{view}.{fmt}"'''})`

**Validacije i eksplicitne greške:**

- `raise HTTPException(422, str(exc)) from exc`

## Detaljne Pydantic šeme

Sljedeći modeli su stvarni ugovori, ne nova projektna specifikacija. Liste dict u Charter/ReviewIn nisu stroga unutrašnja validacija svakog polja aktivnosti. Extra polja su u pravilu ignorisana, osim AIPlan/Task/KPI gdje je extra=forbid. Strogi int je eksplicitan samo na TEST revision/index zahtjevima. JSON Schema s kompletnim granicama i referencama je i u `inventari/openapi.json`.

### Model `SaveRequest` — `mevan_test_workspace_api.py:20`

- `workspace: dict`
- `expected_revision: StrictInt`


### Model `ApprovalRequest` — `mevan_test_workspace_api.py:25`

- `expected_revision: StrictInt`
- `company_index: StrictInt`
- `diagnostic_index: StrictInt`


### Model `ActualIn` — `project_actuals.py:8`

- `period: str = Field(min_length=4, max_length=40)`
- `name: str = Field(min_length=3, max_length=160)`
- `category: Literal['operating_saving', 'contribution_margin', 'avoided_cost', 'working_capital_release']`
- `amount_km: Decimal = Field(ge=0, le=100000000000, decimal_places=2)`
- `evidence_reference: str = Field(min_length=3, max_length=1000)`
- `calculation_note: str = Field(min_length=10, max_length=2000)`
- `source_owner: str = Field(min_length=2, max_length=160)`
- `consultant_confirmed: bool = False`
- `independent_verification: bool = False`


### Model `Task` — `project_ai_pack.py:6`

- `phase: str = Field(min_length=3, max_length=100)`
- `name: str = Field(min_length=8, max_length=300)`
- `owner: str = Field(min_length=3, max_length=100)`
- `due: str = Field(min_length=3, max_length=100)`
- `deliverable: str = Field(min_length=8, max_length=300)`
- `acceptance: str = Field(min_length=8, max_length=300)`


### Model `KPI` — `project_ai_pack.py:15`

- `name: str = Field(min_length=3, max_length=100)`
- `formula: str = Field(min_length=5, max_length=300)`
- `source: str = Field(min_length=3, max_length=200)`
- `frequency: str = Field(min_length=3, max_length=80)`
- `owner: str = Field(min_length=3, max_length=100)`
- `baseline: None = None`
- `target: None = None`


### Model `AIPlan` — `project_ai_pack.py:25`

- `methodology: str = Field(min_length=5, max_length=250)`
- `rationale: str = Field(min_length=15, max_length=1000)`
- `proposed_duration_weeks: int = Field(ge=2, le=52)`
- `hypotheses: list[str] = Field(min_length=1, max_length=8)`
- `validation_checks: list[str] = Field(min_length=2, max_length=15)`
- `activities: list[Task] = Field(min_length=3, max_length=35)`
- `kpis: list[KPI] = Field(min_length=1, max_length=8)`
- `risks: list[str] = Field(min_length=1, max_length=10)`


### Model `CandidateInput` — `project_candidates.py:4`

- `analysis: dict`


### Model `Charter` — `project_execution.py:57`

- `report_mode: Literal['real', 'demo'] = 'real'`
- `problem: str = Field(min_length=10, max_length=4000)`
- `objective: str = Field(min_length=10, max_length=4000)`
- `scope: str = Field(min_length=3, max_length=4000)`
- `methodology: str = Field(min_length=3, max_length=300)`
- `assumptions: list[str] = Field(default_factory=list, max_length=30)`
- `required_checks: list[str] = Field(default_factory=list, max_length=30)`
- `baseline_verified: bool = False`
- `targets_approved: bool = False`
- `checks_completed: bool = False`
- `activities: list[dict] = Field(default_factory=list, max_length=100)`
- `kpis: list[dict] = Field(default_factory=list, max_length=30)`
- `financial_effects: list[dict] = Field(default_factory=list, max_length=30)`


### Model `ProjectIn` — `project_execution.py:72`

- `company_id: str = Field(min_length=1, max_length=100)`
- `diagnostic_id: str = Field(min_length=1, max_length=100)`
- `title: str = Field(min_length=5, max_length=200)`
- `charter: Charter`


### Model `ReviewIn` — `project_execution.py:78`

- `week: str = Field(pattern='^\\d{4}-W\\d{2}$')`
- `activities: list[dict] = Field(default_factory=list, max_length=100)`
- `kpi_measurements: list[dict] = Field(default_factory=list, max_length=50)`
- `blockers: list[str] = Field(default_factory=list, max_length=50)`
- `decisions: list[str] = Field(default_factory=list, max_length=50)`
- `note: str = Field(default='', max_length=4000)`


### Model `CandidateDraftIn` — `project_execution.py:200`

- `company_id: str = Field(min_length=1, max_length=100)`
- `diagnostic_id: str = Field(min_length=1, max_length=100)`
- `analysis: dict`
- `ratings: dict`
- `expected_revision: int = Field(ge=0)`
- `version: int = Field(default=1, ge=1, le=1)`


### Model `Benefit` — `project_finance.py:6`

- `name: str = Field(min_length=3, max_length=160)`
- `category: Literal['operating_saving', 'contribution_margin', 'avoided_cost', 'working_capital_release']`
- `amount_km: Decimal = Field(ge=0, le=100000000000)`
- `source: str = Field(min_length=3, max_length=500)`
- `assumption: str = Field(min_length=3, max_length=500)`
- `evidence_status: Literal['estimated', 'consultant_confirmed', 'independently_verified'] = 'estimated'`


### Model `Scenario` — `project_finance.py:20`

- `name: Literal['pesimistični', 'realni', 'optimistični']`
- `implementation_cost_km: Decimal = Field(ge=0, le=100000000000)`
- `annual_running_cost_km: Decimal = Field(ge=0, le=100000000000)`
- `benefits: list[Benefit] = Field(min_length=1, max_length=30)`


### Model `FinancialModel` — `project_finance.py:26`

- `scenarios: list[Scenario] = Field(min_length=3, max_length=3)`
- `currency: Literal['KM'] = 'KM'`


### Model `Rating` — `project_planner.py:9`

- `value: int = Field(ge=0, le=5)`
- `rationale: str = Field(min_length=5, max_length=1500)`
- `evidence_ids: list[str] = Field(default_factory=list, max_length=30)`


### Model `CandidateRating` — `project_planner.py:14`

- `candidate_id: str`
- `ratings: dict[str, Rating]`


### Model `RankRequest` — `project_planner.py:18`

- `analysis: dict`
- `ratings: list[CandidateRating]`


### Model `DraftRequest` — `project_planner.py:22`

- `analysis: dict`
- `ratings: list[CandidateRating]`
- `selected_id: str \| None = None`
- `company_id: str = Field(min_length=1, max_length=100)`
- `diagnostic_id: str = Field(min_length=1, max_length=100)`
