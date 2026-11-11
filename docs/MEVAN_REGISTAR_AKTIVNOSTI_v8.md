# MEVAN — registar aktivnosti v9 (2026-11-10)

**Opseg:** isključivo TEST grana `mevan-test-sync-bk-qg-20261110`. Nema promjena produkcije, postojeće baze ni legacy API ruta.

| ID | Aktivnost | Status | Dokaz | Sljedeći korak |
|---|---|---|---|---|
| M-01 | Pet oblasti, 61 kriterij | ZAVRŠENO — odluka | Postojeći katalog | Kalibracija |
| M-02 | 366 ankera | NACRT ZAVRŠEN | CSV v0.2 | Pilot validacija |
| QG-01 | Quality Gate pravila | SPECIFICIRANO | QG specifikacija | Engine + testovi |
| A-01 | Read-only audit | ZAVRŠENO | Potvrđen legacy overwrite | Integracija |
| DEV-01 | Izolovana TEST grana | ZAVRŠENO | mevan-test-sync-bk-qg-20261110 | Održavati izolaciju |
| SYNC-01a | Atomski compare-and-swap modul | KOD NAPISAN | mevan_sync_guard.py | Izvršiti testove |
| SYNC-01b | Jedinični testovi | NAPISANO, NEPOTVRĐENO | tests/test_sync_guard.py (6 testova) | CI rezultat |
| CI-01 | Automatsko testiranje | KONFIGURACIJA DODANA, RUN NIJE POTVRĐEN | .github/workflows/mevan-sync-test.yml | Provjeriti pokretanje i log |
| SYNC-02 | TEST API + obrada konflikta u UI | PREOSTALO | — | Integracija bez legacy overwrite |
| BK-01 | Potpun backup i restore | PREOSTALO | — | Izolovan test povrata |
| QG-02 | Quality Gate engine | PREOSTALO | — | Implementacija |
| QA-01 | Integracioni testovi | PREOSTALO | — | Sintetički podaci |
| PILOT-01 | Metodološki pilot | PREOSTALO | — | Nakon sigurnosnih kontrola |

## Pravilo statusa
KOD NAPISAN nije isto što i TESTIRANO; TESTIRANO nije isto što i INTEGRISANO; INTEGRISANO u TEST nije isto što i ODOBRENO ZA PRODUKCIJU.

## Dopuna — sljedeći razvojni korak
- SYNC-01a: lokalno izvršeno šest testova na rekonstruisanoj kopiji modula; 6/6 prolaz. To nije potvrda GitHub CI ni integracionog testa izvornog repozitorija.
- SYNC-API-01: dodan `mevan_test_workspace_api.py` kao **nemontirani TEST prototip** sa GET/PUT i HTTP 409. Nije uključen u postojeći server.
- Sigurnosni uslov: TEST router ne smije se montirati dok nisu ugrađeni autentikacija, CSRF/origin provjera i izolovana baza; postojeće rute ostaju netaknute.
- Sljedeće: integracioni test na zasebnoj bazi, sigurnosna kontrola, obrada 409 u TEST klijentu.

## Dopuna — sigurnost TEST API-ja
- API-SEC-01: **KOD NAPISAN** — TEST router sada zahtijeva autentikacijski i origin callback pri kreiranju; nije montiran u server.
- API-QA-01: **TESTOVI NAPISANI, NISU POTVRĐENI** — pet integracionih scenarija (auth, origin, 409, validacija revizije, sigurnosni ugovor).
- CI-02: **KONFIGURACIJA AŽURIRANA** — pokriva oba testna modula, rezultat izvršavanja tek treba potvrditi.
- **Otvoreno:** stvarna TEST integracija sa sesijom i CSRF pravilima, izolovana baza, UI obrada konflikta, backup/restore i QG engine.

## Dopuna — BK-01 (2026-11-10)
- BK-01a: **KOD NAPISAN, NIJE TESTIRAN** — `mevan_test_backup.py` izvozi TEST workspace sa SHA-256 provjerom integriteta.
- BK-01b: **KOD NAPISAN, NIJE TESTIRAN** — vraćanje uz eksplicitnu potvrdu i očekivanu reviziju, kreira novu reviziju.
- BK-QA-01: **TESTOVI NAPISANI, NISU IZVRŠENI** — pet testova integriteta i oporavka u `tests/test_backup_snapshot.py`.
- CI: proširen na novi modul, izvršavanje nije potvrđeno.
- Ograničenja: ovo nije potpuni backup aplikacije/baze/medija/audit loga; ne koristi se na produkciji. Nije ugrađen u HTTP rute.

## Dopuna — QG-02
- QG-02a: **KOD NAPISAN, NIJE IZVRŠEN** — `mevan_report_gate.py`, BLOCK/WARN/PASS za završni izvještaj, veza s odobrenom revizijom, 61 kriterij, konsultant, kritični rizici O14/L09/M08, finansijske tvrdnje.
- QG-QA-01: **TESTOVI NAPISANI, NISU IZVRŠENI** — 5 testova u `tests/test_report_gate.py`.
- CI konfiguracija ažurirana; rezultat izvršavanja nije potvrđen.
- **Ograničenja:** ovo je TEST politika; nema zaključavanja stvarne revizije, provjere stvarnih izvora, odobravanja izvještaja niti integracije s generisanjem PDF/DOCX.

## Dopuna — QG regresija i CI status
- QG-02b: **KOD IZMIJENJEN** — zapisi bez dokaza i simulirani zapisi sada generišu upozorenja; tip finansijskih tvrdnji se validira.
- QG-QA-02: **3 REGRESIJSKA TESTA NAPISANA, NISU IZVRŠENA** — ukupno 8 testova za report gate.
- CI: za posljednji commit GitHub status i lista workflow runova su prazni. **Nije potvrđeno da su testovi izvršeni**.
- Nema integracije s odobravanjem izvještaja ni promjena produkcije.

## Dopuna — QG pouzdanost, 2026-11-10
- QG-02c: **KOD IZMIJENJEN, NIJE TESTIRAN** — samoprocjena, dokumentovano-neprovjereni dokaz, N/P i simulacija (uključujući `is_simulated` zastavicu) generišu upozorenja; ne mogu proći kao čisti PASS.
- QG-QA-03: **3 NOVA TESTA NAPISANA, NISU IZVRŠENA** — sada 11 report gate testova.
- Ograničenje: `approved_revision` je trenutno ulazni parametar, nije provjeren protiv potpisane/immutable revizije; integracija s odobravanjem izvještaja **NIJE ZAVRŠENA**.
- CI status nije potvrđen; produkcija netaknuta.

## Dopuna — AP-01, nepromjenjivi TEST snimak
- **KOD NAPISAN, NIJE IZVRŠEN:** `mevan_test_approval.py` zapisuje snapshot uz reviziju, SHA-256, konsultanta i vrijeme u posebnu `diagnostic_approvals_test` tabelu.
- **5 TESTOVA NAPISANO, NISU IZVRŠENI:** snapshot ostaje isti nakon promjene workspace-a; zastarjela revizija, nedostajući konsultant, izmijenjen snimak i izolacija legacy tabele.
- **VAŽNO:** ovo je tehnički snapshot/atest revizije, **ne** konačno stručno odobrenje. Quality Gate još nije obavezno povezan s kreiranjem snimka i izvještajima; sam SHA-256 ne dokazuje autentičnost protiv zlonamjerne izmjene baze.
- CI konfiguracija proširena; rezultat izvršavanja nije potvrđen. Produkcija netaknuta.

## Dopuna — RM-01 TEST manifest izvještaja
- **KOD NAPISAN, NIJE TESTIRAN:** `mevan_test_report_manifest.py` učitava odobreni snapshot iz baze po ID-u, čita Quality Gate zapise iz odabrane dijagnostike i odbija BLOCK/WARN. Ne prihvata nezavisno dostavljene zapise niti reviziju.
- **4 TESTA NAPISANA, NISU IZVRŠENA:** nedostajući zapisi, BLOCK, WARN, PASS sa vezom na SHA-256 i reviziju.
- **OGRANIČENJE:** READY_FOR_TEST_RENDER je samo manifest, nema stvarnog generisanja dva izvještaja ni publikacije; izvorna odobravanja još ne zahtijevaju QG i mogu zaključati nepotpun snapshot. Nema produkcijske integracije.
- CI konfiguracija ažurirana; status izvršavanja još nije potvrđen.

## Dopuna — AP-QG-02
- **KOD IZMIJENJEN, NIJE IZVRŠEN:** `approve_workspace` zahtijeva indekse kompanije/dijagnostike i evaluira `evaluate_report_gate` u istoj transakciji, prije zapisivanja odobrenog snimka.
- BLOCK i WARN onemogućavaju kreiranje novog odobrenja; nedostajući Quality Gate podaci blokiraju.
- Testovi `test_approval.py` i `test_report_manifest.py` prilagođeni novom ugovoru; dodana 2 negativna scenarija.
- **OTVORENO:** integracioni testovi nisu potvrđeni; postojeća odobrenja kreirana prije promjene nisu retroaktivno poništena; API/UI i stvarni DOCX izlazi nisu povezani. Ovo je TEST grana.

## Potvrđeno GitHub CI testiranje — 10.11.2026.
- Workflow run: https://github.com/mevan-platform/mevan-diagnostic/actions/runs/42797623238
- Commit: `4469bb5ecb81e15a81aaadd42629f3773b5612b1`.
- **IZVRŠENO I USPJEŠNO: 38/38 testova**, `python -m unittest discover -s tests -p 'test_*.py' -v`. Pregledani stvarni job logovi; job `sync-unit` = success.
- Upozorenja u CI: deprecacija Starlette/httpx i Node.js 20 za GitHub akcije; nisu blokirala testiranje.
- **Novo uočeni rizik za sljedeću iteraciju:** odobrenje trenutno čuva snimak cijelog workspace-a, ali ne identitet odabrane dijagnostike. Manifest prihvata indekse i mogao bi odabrati drugu dijagnostiku iz istog snimka. Potrebno trajno vezati odobrenje za konkretan dijagnostički ID prije izvještaja.
- Testovi ne potvrđuju stvarno generisanje DOCX, produkcijsku integraciju, nezavisnu verifikaciju izvora niti sigurnost deploya.
