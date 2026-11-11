> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: sigurnosne kontrole iz koda, dokazi, rizici i izostale zaštite.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — sigurnost, granice zaštite i rizici

## Model prijetnji i stvarna granica

Privatni single-admin demonstracijski server nije potvrđena višekorisnička produkcijska platforma. Sve kompanije iste instance su dostupne istom loginu. Nema tenant ACL, korisničkih uloga, row-level security, organizacijskog membershipa ili scoped ključeva po kompaniji. company_id/diagnostic_id su identifikatori, ne autorizacija. Supabase/PG RLS nije pronađen; ne zaključivati da izolacija postoji iz filtera dashboarda.

## Kontrole u kodu i granice dokaza

| Površina | Kontrola u kodu | Izvor | Dokaz/ograničenje |
|---|---|---|---|
| Startup konfiguracija | E-mail neprazan, lozinka>=12, secret>=32 | `server.py:14`–`:18` | Preflight traži>=16 i odbija placeholders; startup nije politika kompleksnosti |
| Login | HMAC compare e-mail/lozinke iz env-a; token ts.MAC, 15 min | `server.py:84`,`:101` | Nema hasha users lozinki jer nema user baze; env je osjetljiv |
| Sesija | HMAC-SHA256 potpis ident|expiry, ident=prvih 16SHA256 email | `server.py:67`,`:71` | Cookie nije enkripcija; 8 h, nema server session store/revoke/MFA |
| Cookie | HttpOnly, Secure default 1, SameSite=Strict, max_age 8 h | `server.py:121` | Secure 0 samo lokalni HTTP; ne dokazuje TLS proxy postavku |
| Brute-force | Do 8 neuspjelih pokušaja/IP u 900 s, in-memory deque | `server.py:111` | Restart/više radnika briše/razdvaja stanje; nema distribuiranog limiter-a ili CAPTCHA |
| Login CSRF | Potpisani timestamp token iz forme, ne Origin | `server.py:84`,`:101` | Nije jednokratan niti vezan uz individualnu sesiju; stari token izvan 15 min odbijen |
| Mutacije | same_origin: eksplicitni public origin ili base_url; Origin tačno, Referer prefix expected/ | `server.py:37`, `project_execution.py:51` | Nema univerzalnog synchronizer CSRF tokena za sve API-je; postaviti fiksni origin/hosts iza proxya |
| Autorizacija API-ja | logged/guard ili TEST Depends(require_auth) | `mevan_test_workspace_api.py:41` | Sva prava istog admina; ne per-company |
| HTTP zaglavlja | no-store, nosniff, DENY, no-referrer; HSTS opcionalan | `server.py:22` | CSP samo frame-ancestors na home; nije strogi script-src CSP, inline JavaScript postoji |
| SQL | Parametrizovane vrijednosti ? / %s | `project_execution.py:218`, `server.py:147` | Nije izvršen potpun SQLi pentest; helper PRAGMA imena iz vlastitog sqlite_master nisu korisnički SQL |
| Validacije | Pydantic rasponi, tijela zahtjeva i liste limiti, statusni gate, revizije | [API specifikacija](FUNCTIONAL_SPECIFICATION.md) | JSON dict unutrašnjosti i neki stateless finansijski ValidationError putevi slabije obrađeni |
| Izvještaji/XSS | esc/xmlEsc, textContent; ReportLab escape, python-docx text | `index.html:55`, `approved_reports.py:166` | Nije potpuni DOM XSS audit; direktni innerHTML/template putanje postoje |
| Finansijski retry | UUIDv5 canonical identity, BEGIN IMMEDIATE, PK, audit ista transakcija | `project_execution.py:389`, `project_actuals.py:25` | Ne detektuje poslovnu laž ili sve preklapajuće periode; novi key može označiti novi događaj |
| Snimak | SHA256 kanonskog JSON-a i provjera pri čitanju; v2 mode/model | `mevan_test_approval.py:17`,`:90` | Hash u istoj DB nije vanjski potpis; DB operator može promijeniti payload i hash; zasebna metadata nije sva digest-bound |
| Backup | SQLite backup API, integrity_check, refuse overwrite | `backup_restore.py:24` | Nema enkripcije, rasporeda/offsite ili vraćanja zasebnog PG/priloga |
| AI ključ | Samo serverski env, urllib Authorization; nema ključa u HTML-u | `server.py:241`, `project_ai_pack.py:56` | Prompt injection ograničen promptom, ne dokazano uklonjen; AI dobija korisničke nalaze/dokaze |
| Container | Ne-root user, compose read_only, no-new-privileges, loopback port | `Dockerfile:11`, `compose.yaml:1` | Nije izvršen novi image/CVE/live audit; bazni image i pip nisu digest/lock pinovani |

## SQL/SQLite/PostgreSQL razlike važne za sigurnost

SQLite file štiti samo OS/filesystem/hosting; nema RLS ili instance user ACL. Projektne konekcije uključuju FK, ali legacy/TEST pomoćnici ne uključuju globalnu FK politiku. Optional PG put se odnosi samo na candidate_drafts; URL s pravima operatora je tajna i ne smije u dokumente/logove. Nema pronađene PG migracije/RLS definicije. URL izbor nije automatska migracija cijele aplikacije u PG. Actual-effects idempotentna konkurentnost testirana je SQLite-om, ne udaljenim PG-om.

## Server validacija i kvaliteta podataka

PASS je tehnički gate, ne potvrda stvarnosti. Za provjeren status traži metapodatke i audit referencu, ne preuzima/provjerava eksterni dokument. N/P razlog/ime su tekst, bez novog kriptografskog potpisa odobravatelja. DEMO mode veže se uz snimak i izvoz; helper detektuje rezervni ID/oznake simulacije, ali ne može dokazati da proizvoljno uneseni ljudski tekst nije izmišljen. Stvarni gate nije oslabljen za demo; eksplicitni demo put drugačije zaključava simulaciju i ne odobrava stvarnu implementaciju.

Legacy workspace ima površinsku validaciju i JSON extra polja. Neke Pydantic liste su dict bez strogog modela svakog elementa. Projektni active-unique je aplikacijski SELECT i može imati konkurentni rub; statusni prijelazi nisu svi CAS. Nema retroaktivnog čišćenja podataka ili automatskog popravljanja te metodologije ovim zadatkom.

## XSS, import i nepouzdani sadržaj

Glavni frontend sastavlja HTML stringove i većinom koristi esc/xmlEsc; projektni/dashboard/Guided ekran često textContent. Potrebno je naknadno pregledati svaki direktni innerHTML interpolacijski put prije javnog multiuser izlaganja, posebno AI odgovor, import i reference. Ovaj dokument ne označava dokazan exploit bez reprodukcije. DOCX/PDF tekst se escape-uje odgovarajućem rendereru; to nije dokaz zaštite pri otvaranju svakog vanjskog fajla. Uploada pravih dokumenata nema; source note je tekst. Import JSON može promijeniti cijeli lokalni workspace, restore cijeli legacy workspace, zato ne koristiti neprovjerene kopije na stvarnim podacima.

## Botovi, administracija i tajne

Registracija/bot signup/e-mail verification/reset nisu implementirani, pa njihove zaštite nisu „prošle”. Login je jedini javni formular s autentifikacijskom mutacijom; health je javni liveness. Postojeći in-memory limiter nije produkcijska zaštita od distribuiranih napada. Admin panel za ključeve ili korisnike ne postoji. .env je gitignored, ali postojeći praćeni .env.example ima stvarni e-mail, zbog čega je iz source archive predaje namjerno izostavljen. Nova dokumentacija koristi example.invalid i prazne tajne. Nisu čitane žive env tajne ili Render credentials. Ne uključivati deploy hook, API key, cookie token, dump stvarne baze ili korisničke priloge u Claude predaju.

## Backup, restore i audit

Legacy JSON sadrži workspace bez audit redova; TEST snapshot samo TEST workspace; puni SQLite backup sve redove iste baze, uključujući audit/projekte/odobrenja. Opcionalni PG/vanjski prilozi izvan toga. SQLite integrity_check provjerava konzistentnost datoteke, ne istinitost poslovnih nalaza ili prava pristupa. Audit je append-only u aplikacijskim rutama, ali nije SQL-om zabranjen UPDATE/DELETE DB operatoru i nije WORM. Legacy/AI/login i projektni audit su različite tabele; TEST approval/restore nema isti potpuni audit događaj kao projektne mutacije. Rok čuvanja i šifrovanje nisu implementirani.

## Šta je testirano, a šta ostaje otvoreno

Sačuvane regresije provjeravaju auth/origin, neispravan token/payload/reviziju, idempotentnost/konkurentni retry, rollback audita, hash-integritet, DEMO odvajanje i negaciju tvrdnje nezavisne verifikacije. Nisu potpuni pentest, nezavisni sigurnosni audit, test žive infrastrukture, TLS konfiguracije, stvarnog AI prompt injection ponašanja ili produkcijske tenant izolacije. Nema novog sigurnosnog izvršavanja u dokumentacijskom zadatku. Za konkretne testne metode vidjeti [QA inventar](TESTING_AND_QA.md).

Prioritet prije rada sa stvarnim nepovezanim klijentima: odlučiti instance/tenant model, provesti sigurnosnu reviziju, sesijsku revokaciju/uloge, distribuirani rate limit, strože JSON šeme/body limite, provjeru svih HTML puteva, šifrovani i testirani multi-store backup. Ovo su preporuke za budući odobreni opseg, ne nove implementirane kontrole.
