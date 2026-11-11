> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: svi testovi i očekivanja, sačuvani rezultati i otvoreni manualni scenariji.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — testiranje i osiguranje kvaliteta

## Šta predstavlja rezultat

Ovo je inventar postojećeg koda testova i sačuvanih rezultata, bez ponovnog izvršavanja uspješnog paketa. Definicija testa nije dokaz da je izvršen na živoj infrastrukturi. AST inventar broji 125 funkcija/metoda `test_*`; parametrizacija/unittest daju 168 slučajeva u sačuvanom JUnit-u. Browser skripte i Word generator nisu iste pytest metode i opisani su odvojeno. Svaki ID u nastavku vodi do stvarnog source:line; očekivanja su doslovni assert izrazi, ne proizvoljan „passed”.

## Potvrđene serije i granice

| Serija | Zabilježen rezultat | Dokaz | Granica |
|---|---|---|---|
| Prvi paket, prije paketa 2 | 136 prolaza. | Prethodni CI run 42899507229 na `2a31e358c1d7c72f79c4acb25907dabd9ba34fb5` i lokalni baseline log. | Ne pokriva kompletan novi Guided browser tok. |
| Drugi paket, zajednička regresija | 168 prolaza, jedno upozorenje Starlette/httpx; 24, 30 sekundi. | Sačuvani pytest-release log i JUnit XML. | Sintetičke privremene SQLite baze i offline/mock odgovori. |
| Završni Word QA | 12/12 dokumenata prolazi ZIP, XML i sadržajne provjere. | Sačuvani word-final.log. | Nije vizuelni Word render. |
| Mobilni tok prvog paketa | Prolazi na 390 × 844: validacija pregleda, četiri izvoza, rangiranje, stale konflikt i retry efekta. | Sačuvani browser-release.log. | Lokalni Chromium, ne stvarni telefon ili stvarni AI. |
| Mobilni tok drugog paketa | Prolaze trajno čuvanje, N/P, projekat, plan, četiri DEMO izvoza i dodatni legacy putevi. | Sačuvani browser-complete.log. | Ovaj dodatni browser test nije CI korak. |
| Vizuelni PDF uzorci | Pregledani su direktorski naslov/radar, detaljni izvori i potpuno N/P skup. | Raniji previews i izvještaj. | Reprezentativne stranice, ne svi mogući unosi. |
| Stvarni AI, Render i udaljeni PostgreSQL | Neprovjereno u ovom okruženju. | Nema odgovarajućeg izvršenog dokaza. | Ne smije se navesti kao passed. |

U direktoriju `dokazi/` ovog paketa nalaze se kopije navedenih sintetičkih logova i JUnit XML-a. Originalni dokazi iz prethodne analize ostaju netaknuti.

Puna Python regresija nije ponavljana nakon završnih UI-only dopuna print/Word oznaka i povezivanja režima; za njih su ponovljeni Word QA i ciljani browser. Raniji neuspjeli pokušaji ostaju u arhivi, ne prepisuju se: accessibility label i N/P source notes su ispravljeni, historijski test eksplicitno vezan uz policy 1. Izvorne Word provjere nisu uklonjene: popravljen je extractor da kompajlira cijelu stvarnu skriptu umjesto rezanja na startup pozivu.

Paket 2 sačuvao je 31+2+36 ranijih artefakt hashova. U ovu predaju uključeni su samo odabrani sintetički logovi/JUnit i rezultatski metapodaci, ne stvarne baze, cookies ili credentials. Stari izvještaji čuvaju historijske tadašnje nalaze; kasnija dopuna ih ne prepravlja.

## Porodice provjera

- Autentifikacija i HTTP: provjeravaju se zaštićeni ekrani, prijavni token, Origin/Referer, odjava i neispravni zahtjevi. Očekuju se odgovarajući odgovori 401, 403 ili preusmjerenje. `test_browser_readiness.py` provjerava HTTP odgovore, a ne izvršavanje interfejsa u pravom pregledniku.
- Radni prostori: testiraju se prvi upis, očekivani hash ili revizija, konkurentni CAS, prevelik payload i odbijanje zastarjele revizije bez prepisivanja. TEST upis mora ostaviti legacy tabelu neizmijenjenom.
- Gate i snimci: provjeravaju se 61 jedinstven kriterij, ocjene, dokazi, rizici, simulacije, finansijske tvrdnje i integritet SHA-256. Pogrešna dijagnostika ili zastarjela revizija ne smiju dobiti odobrenje. Historijski snimci v1 ostaju čitljivi.
- Konsultantski pregled iz prvog paketa: sedam polja popunjenih sa „x”, zamjenskim ili prekratkim tekstom mora biti odbijeno. Valjan bosanski primjer prolazi tehničku potpunost. Ranije odobren kratak sadržaj ostaje dostupan za čitanje.
- Finansijski efekti iz prvog paketa: ponavljanje istog zahtjeva za 4.000 KM mora vratiti jedan zapis i jedan audit događaj. Isti ključ s drugim sadržajem daje 409, dok novi ključ može označiti zaseban zakonit događaj. Testira se i konkurentni retry te rollback nakon neuspjelog audit upisa.
- N/P iz drugog paketa: testira se izuzimanje svakog od pet modula, miješanog skupa i svih kriterija. Očekivani indeks računa se nezavisno u testu. Razlog i konsultant moraju se prenijeti u sva četiri izvještaja; prazan skup je neocjenjiv, a nedokazani primjenjivi kriterij i dalje blokira stvarni izvještaj.
- DEMO iz drugog paketa: režim mora ostati vezan uz snimak i manifest. Promjena query parametra ne uklanja oznaku. Oznaka je na svakoj PDF stranici i u DOCX zaglavlju/podnožju. Miješanje simulacije i provjerenih tvrdnji, nedostajući dokazi i pokušaj stvarne implementacije DEMO projekta moraju biti odbijeni.
- Vođeni tok: bilješke o tri izvora, aktivni korak, izabrani projekat i plan moraju ostati poslije spremanja i osvježavanja. Kasniji rad ne smije promijeniti zamrznuti obračun zaključanog snimka. Neispravna collection struktura mora biti odbijena bez prepisivanja sačuvanog workspacea.
- Projekti i finansije: provjeravaju se statusni prijelazi, audit, zaključavanje chartera, stvarne ISO sedmice, Decimal obračuni, razlika procjene i ostvarenog efekta, izvještaji i portfolio rokovi.
- Sigurnosne kopije: provjeravaju se WAL sadržaj, integritet, nepostojeća ili neispravna baza i zabrana prepisivanja odredišta. TEST JSON snapshot ima zasebne provjere hasha, potvrde i očekivane revizije.

## Potpuni inventar definicija testova

Za unittest očekivanja su pozivi assertEqual/assertRaises itd.; pytest koristi assert/raises. Parametrize dekoratori i fixture setup su u izvornom fajlu/JSON inventaru. Ovdje se navodi svaka definicija i svi eksplicitni assert izrazi izdvojeni iz nje; očekivanje složenog helpera treba čitati zajedno s navedenim sourceom, ne smatrati generičkom potvrdom kvaliteta.

### QA-001 — `test_4000_twice_is_one_effect_and_one_audit`

Lokacija: `test_actual_effect_idempotency.py:43`. **Svrha i očekivano ponašanje:** Ponavljanje zahtjeva za 4.000 KM ostavlja jedan efekat i jedan audit događaj. 

- Očekivanje: `assert a.status_code == b.status_code == 201`
- Očekivanje: `assert a.json()['id'] == b.json()['id']`
- Očekivanje: `assert not a.json()['replayed'] and b.json()['replayed']`
- Očekivanje: `assert len(data['entries']) == 1`
- Očekivanje: `assert data['summary']['consultant_confirmed_recurring_km'] == 4000`
- Očekivanje: `assert sum((e['action'] == 'actual_effect_recorded' for e in events)) == 1`

### QA-002 — `test_simultaneous_retries_create_exactly_one_row`

Lokacija: `test_actual_effect_idempotency.py:57`. **Svrha i očekivano ponašanje:** Istovremeni identični retry zahtjevi stvaraju tačno jedan red. 

- Očekivanje: `assert [r.status_code for r in responses] == [201] * 6`
- Očekivanje: `assert len({r.json()['id'] for r in responses}) == 1`
- Očekivanje: `assert sum((not r.json()['replayed'] for r in responses)) == 1`
- Očekivanje: `assert f.client.get(url).json()['summary']['consultant_confirmed_recurring_km'] == 4000`
- Očekivanje: `assert sum((e['action'] == 'actual_effect_recorded' for e in events)) == 1`

### QA-003 — `test_distinct_events_and_changed_evidence_are_preserved`

Lokacija: `test_actual_effect_idempotency.py:74`. **Svrha i očekivano ponašanje:** Različiti događaji i izmijenjeni dokazni sadržaj ostaju zasebni legitimni zapisi. 

- Očekivanje: `assert all((r.status_code == 201 for r in responses))`
- Očekivanje: `assert len({r.json()['id'] for r in responses}) == 4`
- Očekivanje: `assert len(f.client.get(url).json()['entries']) == 4`

### QA-004 — `test_key_cannot_be_reused_for_changed_content`

Lokacija: `test_actual_effect_idempotency.py:83`. **Svrha i očekivano ponašanje:** Isti idempotentni ključ ne smije se ponovo koristiti za drugi sadržaj. 

- Očekivanje: `assert post(f, url, key='isti-dogadjaj').status_code == 201`
- Očekivanje: `assert post(f, url, effect(amount_km=5000), key='isti-dogadjaj').status_code == 409`
- Očekivanje: `assert f.client.get(url).json()['summary']['consultant_confirmed_recurring_km'] == 4000`

### QA-005 — `test_key_is_scoped_to_project`

Lokacija: `test_actual_effect_idempotency.py:90`. **Svrha i očekivano ponašanje:** Isti događajni ključ ima zaseban identitet u svakom projektu. 

- Očekivanje: `assert a.status_code == b.status_code == 201 and a.json()['id'] != b.json()['id']`

### QA-006 — `test_existing_legacy_rows_are_not_modified_or_merged`

Lokacija: `test_actual_effect_idempotency.py:97`. **Svrha i očekivano ponašanje:** Raniji legacy redovi ne smiju se mijenjati ili automatski spajati. 

- Očekivanje: `assert len(f.client.get(url).json()['entries']) == 3`
- Očekivanje: `assert db.execute("SELECT * FROM v4_actual_effects WHERE id LIKE 'legacy-%' ORDER BY id").fetchall() == legacy`

### QA-007 — `test_failed_audit_rolls_back_effect_and_allows_retry`

Lokacija: `test_actual_effect_idempotency.py:109`. **Svrha i očekivano ponašanje:** Neuspješan audit upis poništava efekat i omogućava kasniji retry. 

- Očekivanje: `assert f.client.get(url).json()['entries'] == []`
- Očekivanje: `assert post(f, url, key='retry-poslije-kvara').status_code == 201`

### QA-008 — `test_invalid_payload_and_key_are_rejected_without_writes`

Lokacija: `test_actual_effect_idempotency.py:123`. **Svrha i očekivano ponašanje:** Neispravni payload i događajni ključ odbijaju se bez upisa. 

- Očekivanje: `assert post(f, url, effect(amount_km=-1)).status_code == 422`
- Očekivanje: `assert post(f, url, key='nedozvoljena oznaka').status_code == 422`
- Očekivanje: `assert f.client.get(url).json()['entries'] == []`

### QA-009 — `test_live_wal_backup_restore_and_no_overwrite`

Lokacija: `test_backup_restore.py:8`. **Svrha i očekivano ponašanje:** SQLite backup vraća i WAL sadržaj te odbija prepisivanje odredišta. 

- Očekivanje: `self.assertEqual(check.execute('SELECT value FROM entries').fetchone()[0], 'METALPRO demo')`

### QA-010 — `test_corrupted_source_rejected`

Lokacija: `test_backup_restore.py:27`. **Svrha i očekivano ponašanje:** Neispravna izvorna SQLite baza mora biti odbijena. 

- Očekivanje: `self.assertFalse((root / 'backup.db').exists())`

### QA-011 — `test_missing_source_rejected`

Lokacija: `test_backup_restore.py:36`. **Svrha i očekivano ponašanje:** Nepostojeći izvor sigurnosne kopije mora biti odbijen. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-012 — `test_ui_auth_navigation_and_assets`

Lokacija: `test_browser_readiness.py:7`. **Svrha i očekivano ponašanje:** HTTP provjera potvrđuje prijavu, zaštićene ekrane i dostupnost HTML-a. 

- Očekivanje: `assert r.status_code == 303`
- Očekivanje: `assert client.get('/api/v4/dashboard').status_code == 200`
- Očekivanje: `assert client.get('/api/v4/projects').status_code == 200`
- Očekivanje: `assert client.post('/logout', headers={'Origin': 'http://testserver'}, follow_redirects=False).status_code == 303`
- Očekivanje: `assert client.get('/api/v4/dashboard').status_code == 401`
- Očekivanje: `assert r.status_code in (302, 303, 307), route`
- Očekivanje: `assert '/login' in r.headers['location']`
- Očekivanje: `assert r.status_code == 200, route`
- Očekivanje: `assert '<html' in r.text.lower() or '<!doctype' in r.text.lower(), route`
- Očekivanje: `assert len(r.text) > 1000, route`

### QA-013 — `test_dashboard_route_and_page`

Lokacija: `test_dashboard.py:3`. **Svrha i očekivano ponašanje:** Dashboard API i zaštićena HTML stranica vraćaju očekivani sadržaj. 

- Očekivanje: `assert '/api/v4/dashboard' in routes`
- Očekivanje: `assert '/api/v4/dashboard' in page`
- Očekivanje: `assert 'Nezavisno verificirani' in page`
- Očekivanje: `assert 'textContent' in page`

### QA-014 — `test_dashboard_no_aggregated_financial_amounts`

Lokacija: `test_dashboard.py:12`. **Svrha i očekivano ponašanje:** Dashboard ne sabira finansijske iznose neuporedivih perioda. 

- Očekivanje: `assert 'consultant_confirmed_entries_count' in source`
- Očekivanje: `assert 'independently_verified_entries_count' in source`
- Očekivanje: `assert 'sum(json.loads' not in source`

### QA-015 — `test_simulated_cannot_verify`

Lokacija: `test_data_quality_gate.py:4`. **Svrha i očekivano ponašanje:** Simulirani zapis ne smije postati provjeren dokaz. 

- Očekivanje: `self.assertEqual(x['status'], 'blokirano')`
- Očekivanje: `self.assertFalse(x['independently_verified'])`

### QA-016 — `test_unknown_not_zero`

Lokacija: `test_data_quality_gate.py:7`. **Svrha i očekivano ponašanje:** Nepoznati kriterij ne smije imati numeričku nulu umjesto nedostajuće ocjene. 

- Očekivanje: `self.assertEqual(check_record({'criterion_id': 'F05', 'score': 0, 'verification_status': 'nema_podataka'})['status'], 'blokirano')`

### QA-017 — `test_na_approval`

Lokacija: `test_data_quality_gate.py:9`. **Svrha i očekivano ponašanje:** N/P zahtijeva obrazloženje i konsultantsku potvrdu. 

- Očekivanje: `self.assertEqual(check_record({'criterion_id': 'F05', 'verification_status': 'nije_primjenjivo'})['status'], 'blokirano')`

### QA-018 — `test_invalid_ratio`

Lokacija: `test_data_quality_gate.py:11`. **Svrha i očekivano ponašanje:** Nevalidan nazivnik omjernog KPI-ja mora blokirati zapis. 

- Očekivanje: `self.assertEqual(check_record({'criterion_id': 'O01', 'score': 2, 'verification_status': 'samoprocjena', 'kpi_ratio': True, 'denominator': 0})['status'], 'blokirano')`

### QA-019 — `test_duplicate`

Lokacija: `test_data_quality_gate.py:13`. **Svrha i očekivano ponašanje:** Dupla šifra kriterija mora biti otkrivena. 

- Očekivanje: `self.assertEqual(check_batch([{'criterion_id': 'F05'}, {'criterion_id': 'F05'}])['blocked'], 1)`

### QA-020 — `test_simulation_labeled`

Lokacija: `test_data_quality_gate.py:15`. **Svrha i očekivano ponašanje:** Simulacija mora biti označena i ne predstavljati nezavisno provjeren rezultat. 

- Očekivanje: `self.assertEqual(x['status'], 'prolaz')`
- Očekivanje: `self.assertFalse(x['independently_verified'])`

### QA-021 — `test_benefit_requires_basis`

Lokacija: `test_data_quality_gate.py:18`. **Svrha i očekivano ponašanje:** Finansijska korist zahtijeva osnovicu i podatke za obračun. 

- Očekivanje: `self.assertEqual(check_record({'criterion_id': 'F06', 'score': 2, 'verification_status': 'samoprocjena', 'financial_benefit': 100})['status'], 'blokirano')`

### QA-022 — `test_financial_and_effect_audit`

Lokacija: `test_financial_audit.py:6`. **Svrha i očekivano ponašanje:** Promjena finansijskog modela i stvarni efekat ostavljaju audit trag. 

- Očekivanje: `assert r.status_code == 201, r.text`
- Očekivanje: `assert [e['action'] for e in events] == ['created', 'financial_model_created', 'financial_model_updated']`
- Očekivanje: `assert json.loads(events[2]['previous_payload'])['scenarios'][0]['benefits'][0]['amount_km'] == '500'`
- Očekivanje: `assert json.loads(events[2]['new_payload'])['scenarios'][0]['benefits'][0]['amount_km'] == '700'`
- Očekivanje: `assert c.post(base + '/approve-validation', headers=h).status_code == 200`
- Očekivanje: `assert c.put(base + '/charter', json=charter, headers=h).status_code == 200`
- Očekivanje: `assert c.post(base + '/approve-implementation', headers=h).status_code == 200`
- Očekivanje: `assert r.status_code == 201, r.text`
- Očekivanje: `assert c.post(base + '/weekly-reviews', json={'week': '2026-W46', 'note': 'Simulirani pregled'}, headers=h).status_code == 201`
- Očekivanje: `assert events[-2]['action'] == 'actual_effect_recorded'`
- Očekivanje: `assert json.loads(events[-2]['new_payload'])['effect_id'] == eid`
- Očekivanje: `assert events[-1]['action'] == 'weekly_review_created'`
- Očekivanje: `assert json.loads(events[-1]['new_payload'])['week'] == '2026-W46'`
- Očekivanje: `assert c.put(base + '/financial-model', json=model(900), headers=h).status_code == 409`
- Očekivanje: `assert c.post(base + '/weekly-reviews', json={'week': '2026-W46'}, headers=h).status_code == 409`
- Očekivanje: `assert len(c.get(base + '/audit').json()['events']) == len(events)`
- Očekivanje: `assert c.get(base + '/audit').status_code == 401`
- Očekivanje: `assert r.status_code == 200, r.text`

### QA-023 — `test_http_smoke_script_is_bundled`

Lokacija: `test_http_release_smoke.py:3`. **Svrha i očekivano ponašanje:** HTTP smoke skripta mora biti uključena u razvojni paket. 

- Očekivanje: `assert p.exists()`
- Očekivanje: `assert 'TemporaryDirectory' in text and 'MEVAN_DB' in text`
- Očekivanje: `assert 'OPENAI_API_KEY' not in text`

### QA-024 — `test_01_protected`

Lokacija: `test_integration.py:17`. **Svrha i očekivano ponašanje:** Neprijavljeni korisnik ne dobija zaštićeni workspace. 

- Očekivanje: `self.assertEqual(self.client.get('/api/workspace').status_code, 401)`
- Očekivanje: `self.assertEqual(self.client.post('/api/ai/draft', json={}).status_code, 401)`

### QA-025 — `test_02_login_and_persistence`

Lokacija: `test_integration.py:20`. **Svrha i očekivano ponašanje:** Prijava i upis/čitanje workspacea čuvaju očekivano stanje. 

- Očekivanje: `self.assertEqual(bad.status_code, 401)`
- Očekivanje: `self.assertEqual(good.status_code, 303)`
- Očekivanje: `self.assertEqual(self.client.put('/api/workspace', json=payload, headers={'Origin': 'http://testserver'}).status_code, 200)`
- Očekivanje: `self.assertEqual(self.client.get('/api/workspace').json()['workspace'], payload)`
- Očekivanje: `self.assertEqual(self.client.put('/api/workspace', json=payload, headers={'Origin': 'https://evil.test'}).status_code, 403)`
- Očekivanje: `self.assertEqual(self.client.put('/api/workspace', json={'companies': []}, headers={'Origin': 'http://testserver'}).status_code, 400)`

### QA-026 — `test_02b_backup_restore_and_audit`

Lokacija: `test_integration.py:31`. **Svrha i očekivano ponašanje:** Legacy backup, restore i audit imaju odgovarajući JSON tok. 

- Očekivanje: `self.assertEqual(backup.status_code, 200)`
- Očekivanje: `self.assertEqual(backup.json()['format'], 'mevan-backup-v1')`
- Očekivanje: `self.assertEqual(backup.json()['workspace']['companies'][0]['name'], 'METALPRO DEMO')`
- Očekivanje: `self.assertEqual(self.client.post('/api/backup/restore', json=backup.json(), headers={'Origin': 'http://testserver'}).status_code, 400)`
- Očekivanje: `self.assertEqual(self.client.post('/api/backup/restore', json={'format': 'bad'}, headers=headers).status_code, 400)`
- Očekivanje: `self.assertEqual(self.client.post('/api/backup/restore', json=backup.json(), headers=headers).status_code, 200)`
- Očekivanje: `self.assertEqual(self.client.get('/api/workspace').json()['workspace'], backup.json()['workspace'])`
- Očekivanje: `self.assertTrue(any((e['event'] == 'backup_restore' for e in events)))`

### QA-027 — `test_03_ai_without_key_and_logout`

Lokacija: `test_integration.py:43`. **Svrha i očekivano ponašanje:** AI bez ključa ostaje nedostupan, a odjava uklanja pristup. 

- Očekivanje: `self.assertEqual(r.status_code, 503)`
- Očekivanje: `self.assertEqual(self.client.post('/logout', headers={'Origin': 'https://evil.test'}, follow_redirects=False).status_code, 403)`
- Očekivanje: `self.assertEqual(self.client.post('/logout', headers={'Origin': 'http://testserver'}, follow_redirects=False).status_code, 303)`
- Očekivanje: `self.assertEqual(self.client.get('/api/workspace').status_code, 401)`

### QA-028 — `test_61_criteria_and_finance_separation`

Lokacija: `test_metalpro_demo.py:8`. **Svrha i očekivano ponašanje:** METALPRO ima 61 kriterij i odvojene procjene od potvrđenih finansija. 

- Očekivanje: `assert a['coverage']['confirmed'] == 61 and a['coverage']['independently_verified'] == 0`
- Očekivanje: `assert a['index'] == 36.4`
- Očekivanje: `assert {k: v['index'] for k, v in a['dimensions'].items()} == {'F': 38.3, 'O': 34.7, 'P': 35.0, 'L': 42.0, 'M': 33.3}`
- Očekivanje: `assert len(prepare_candidates(a)['candidates']) >= 1`
- Očekivanje: `assert all((x['confirmed_annual_benefit_km'] == 0 and x['confirmed_one_time_benefit_km'] == 0 for x in s['financial_scenarios']))`
- Očekivanje: `assert s['confirmed_annual_km'] == s['confirmed_one_time_km'] == 0`
- Očekivanje: `assert realistic['one_time_working_capital_release_km'] == 160000`
- Očekivanje: `assert realistic['annual_gross_benefit_km'] == 52167`

### QA-029 — `test_metalpro_full_offline_workflow`

Lokacija: `test_metalpro_demo.py:20`. **Svrha i očekivano ponašanje:** Sintetički METALPRO prolazi postojeći offline tok analize, kandidata i projekta. 

- Očekivanje: `assert client.post('/login', data={'csrf_token': token, 'email': 'demo@example.test', 'password': '<sintetička vrijednost iz fixturea>'}, follow_redirects=False).status_code == 303`
- Očekivanje: `assert c.status_code == 200 and c.json()['candidates']`
- Očekivanje: `assert rank.status_code == 200 and rank.json()['candidates'][0]['score'] is not None`
- Očekivanje: `assert d.status_code == 200, d.text`
- Očekivanje: `assert draft['charter']['baseline_verified'] is False`
- Očekivanje: `assert created.status_code == 201, created.text`
- Očekivanje: `assert client.post(root + '/approve-implementation', headers=h).status_code == 409`
- Očekivanje: `assert fin.status_code == 200, fin.text`
- Očekivanje: `assert client.post(root + '/approve-validation', headers=h).status_code == 200`
- Očekivanje: `assert client.post(root + '/weekly-reviews', json={'week': '2026-W46', 'note': 'Nema odobrene implementacije'}, headers=h).status_code == 409`
- Očekivanje: `assert client.post(root + '/actual-effects', json={'period': '2026-11', 'name': 'Simulirani efekat', 'category': 'operating_saving', 'amount_km': 100, 'evidence_reference': 'demo', 'calculation_note': 'Simulacija, bez verifikacije', 'source_owner': 'Demo'}, headers=h).status_code == 409`
- Očekivanje: `assert client.get('/api/v4/dashboard').status_code == 200`
- Očekivanje: `assert client.get(root + '/actual-effects').json()['summary']['independently_verified_km'] == 0`
- Očekivanje: `assert client.get(root).json()['status'] == 'validation'`
- Očekivanje: `assert report.status_code == 200 and report.content.startswith(signature)`

### QA-030 — `test_demo_project_cannot_be_relabelled_or_implemented`

Lokacija: `test_package2_project.py:5`. **Svrha i očekivano ponašanje:** DEMO projekat ne može promijeniti režim ili dobiti stvarno implementacijsko odobrenje. 

- Očekivanje: `assert r.status_code == 201, r.text`
- Očekivanje: `assert f.client.put(base + '/charter', json={**charter, 'report_mode': 'real'}, headers=f.headers).status_code == 409`
- Očekivanje: `assert f.client.put(base + '/charter', json=confirmed, headers=f.headers).status_code == 200`
- Očekivanje: `assert f.client.post(base + '/approve-implementation', headers=f.headers).status_code == 409`
- Očekivanje: `assert f.client.get(base).json()['status'] == 'draft'`
- Očekivanje: `assert f.client.post(base + '/actual-effects', json={'period': '2026-11', 'name': 'DEMO efekat', 'category': 'operating_saving', 'amount_km': 4000, 'evidence_reference': 'Ogledni izvor', 'calculation_note': 'Simulirani obračun efekta', 'source_owner': 'QA'}, headers=f.headers).status_code == 409`
- Očekivanje: `assert report.status_code == 200`
- Očekivanje: `assert 'DEMO — simulirani podaci' in word.sections[0].header.paragraphs[0].text`

### QA-031 — `test_independent_verification_not_claimed`

Lokacija: `test_project_actuals.py:8`. **Svrha i očekivano ponašanje:** Obrazac stvarnog efekta ne prihvata tvrdnju nezavisne verifikacije. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-032 — `test_evidence_required`

Lokacija: `test_project_actuals.py:11`. **Svrha i očekivano ponašanje:** Evidentirani efekat zahtijeva dokaznu referencu. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-033 — `test_pending_not_confirmed`

Lokacija: `test_project_actuals.py:14`. **Svrha i očekivano ponašanje:** Nepotvrđeni efekti ne ulaze u konsultantski potvrđene sume. 

- Očekivanje: `assert s['consultant_confirmed_recurring_km'] == 0 and s['pending_count'] == 1`

### QA-034 — `test_confirmed_separates_working_capital`

Lokacija: `test_project_actuals.py:18`. **Svrha i očekivano ponašanje:** Potvrđeni ponavljajući efekti i jednokratni obrtni kapital ostaju razdvojeni. 

- Očekivanje: `assert s['consultant_confirmed_recurring_km'] == 120.5 and s['consultant_confirmed_one_time_working_capital_km'] == 160000 and (s['independently_verified_km'] == 0)`

### QA-035 — `test_valid_ai_pack_unapproved`

Lokacija: `test_project_ai_pack.py:20`. **Svrha i očekivano ponašanje:** Valjan AI projektni paket ostaje neodobren nacrt. 

- Očekivanje: `self.assertEqual(data['status'], 'DRAFT_REQUIRES_CONSULTANT_APPROVAL')`
- Očekivanje: `self.assertFalse(data['charter']['baseline_verified'])`
- Očekivanje: `self.assertEqual(data['charter']['financial_effects'], [])`
- Očekivanje: `self.assertEqual(len(data['charter']['activities']), 3)`

### QA-036 — `test_reject_fabricated_baseline`

Lokacija: `test_project_ai_pack.py:26`. **Svrha i očekivano ponašanje:** AI projektni paket odbija izmišljenu brojčanu osnovicu. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-037 — `test_reject_extra_financial_claims`

Lokacija: `test_project_ai_pack.py:29`. **Svrha i očekivano ponašanje:** AI projektni paket odbija dodatna polja s finansijskim tvrdnjama. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-038 — `test_selects_ranking_not_fixed_project`

Lokacija: `test_project_ai_pack.py:32`. **Svrha i očekivano ponašanje:** AI paket koristi odabrani rangirani projekat, a ne fiksni naslov. 

- Očekivanje: `self.assertEqual(data['title'], 'Smanjenje škarta')`

### QA-039 — `test_project_audit_history`

Lokacija: `test_project_audit.py:5`. **Svrha i očekivano ponašanje:** Historija projekta čuva kreiranje, izmjene i odobrenja. 

- Očekivanje: `assert response.status_code == 201, response.text`
- Očekivanje: `assert [x['action'] for x in client.get(url).json()['events']] == ['created']`
- Očekivanje: `assert client.put(f'/api/v4/projects/{pid}/charter', json=fixture.charter, headers=fixture.headers).status_code == 200`
- Očekivanje: `assert len(client.get(url).json()['events']) == 1`
- Očekivanje: `assert client.put(f'/api/v4/projects/{pid}/charter', json=edited, headers=fixture.headers).status_code == 200`
- Očekivanje: `assert client.post(f'/api/v4/projects/{pid}/approve-validation', headers=fixture.headers).status_code == 200`
- Očekivanje: `assert [x['action'] for x in events] == ['created', 'charter_edited', 'validation_approved']`
- Očekivanje: `assert json.loads(events[1]['previous_payload'])['objective'] == fixture.charter['objective']`
- Očekivanje: `assert json.loads(events[1]['new_payload'])['objective'] == edited['objective']`
- Očekivanje: `assert client.get('/api/v4/projects/not-a-project/audit').status_code == 404`
- Očekivanje: `assert client.get(url).status_code == 401`

### QA-040 — `test_no_invented_financial_values`

Lokacija: `test_project_candidates.py:5`. **Svrha i očekivano ponašanje:** Kandidat ne dobija izmišljene finansijske iznose. 

- Očekivanje: `self.assertEqual(r['status'], 'DRAFT_NOT_APPROVED')`
- Očekivanje: `self.assertEqual(len(r['candidates']), 1)`
- Očekivanje: `self.assertEqual(r['candidates'][0]['criterion_codes'], ['P01'])`
- Očekivanje: `self.assertEqual(r['candidates'][0]['financial_impact'], 'NIJE_VERIFICIRANO')`

### QA-041 — `test_empty_analysis`

Lokacija: `test_project_candidates.py:12`. **Svrha i očekivano ponašanje:** Prazna analiza vraća praznu listu kandidata. 

- Očekivanje: `self.assertEqual(prepare_candidates({})['candidates'], [])`

### QA-042 — `test_auth_origin_and_gate`

Lokacija: `test_project_execution.py:21`. **Svrha i očekivano ponašanje:** Projektni tok provjerava autentifikaciju, porijeklo zahtjeva i statusne uslove. 

- Očekivanje: `self.assertEqual(self.client.post('/api/v4/projects', json=payload).status_code, 403)`
- Očekivanje: `self.assertEqual(r.status_code, 201)`
- Očekivanje: `self.assertEqual(self.client.post('/api/v4/projects', json=payload, headers=self.headers).status_code, 409)`
- Očekivanje: `self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/approve-implementation', headers=self.headers).status_code, 409)`
- Očekivanje: `self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/approve-validation', headers=self.headers).status_code, 200)`
- Očekivanje: `self.assertEqual(self.client.put(f'/api/v4/projects/{pid}/charter', json=ch, headers=self.headers).status_code, 200)`
- Očekivanje: `self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/approve-implementation', headers=self.headers).status_code, 200)`
- Očekivanje: `self.assertEqual(self.client.put(f'/api/v4/projects/{pid}/charter', json=ch, headers=self.headers).status_code, 409)`
- Očekivanje: `self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/weekly-reviews', json=review, headers=self.headers).status_code, 201)`
- Očekivanje: `self.assertEqual(self.client.post(f'/api/v4/projects/{pid}/weekly-reviews', json=review, headers=self.headers).status_code, 409)`
- Očekivanje: `self.assertEqual(len(data['weekly_reviews']), 1)`
- Očekivanje: `self.assertEqual(data['status'], 'implementation')`

### QA-043 — `test_protected_without_login`

Lokacija: `test_project_execution.py:40`. **Svrha i očekivano ponašanje:** Projektni API ne daje podatke bez prijave. 

- Očekivanje: `self.assertEqual(self.client.get('/api/v4/projects').status_code, 401)`

### QA-044 — `test_financial_separation`

Lokacija: `test_project_finance.py:12`. **Svrha i očekivano ponašanje:** Finansijski kalkulator razdvaja godišnju korist i obrtni kapital. 

- Očekivanje: `assert r['annual_net_benefit_km'] == 10000`
- Očekivanje: `assert r['one_time_working_capital_release_km'] == 160000`
- Očekivanje: `assert r['simple_annual_roi_percent'] == 100`
- Očekivanje: `assert r['simple_payback_months'] == 12`
- Očekivanje: `assert r['confirmed_annual_benefit_km'] == 0`

### QA-045 — `test_missing_scenario_rejected`

Lokacija: `test_project_finance.py:20`. **Svrha i očekivano ponašanje:** Finansijski model bez sva tri scenarija mora biti odbijen. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-046 — `test_unverified_claim_cannot_be_confirmed`

Lokacija: `test_project_finance.py:24`. **Svrha i očekivano ponašanje:** Kalkulator procjena ne može sam potvrditi neprovjerenu korist. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-047 — `test_no_payback_on_negative_net`

Lokacija: `test_project_finance.py:28`. **Svrha i očekivano ponašanje:** Negativan neto efekat ne daje izračunljiv rok povrata. 

- Očekivanje: `assert r['simple_payback_months'] is None`

### QA-048 — `test_no_roi_when_no_investment`

Lokacija: `test_project_finance.py:33`. **Svrha i očekivano ponašanje:** Nula implementacijskog troška ne daje brojčani ROI. 

- Očekivanje: `assert r['simple_annual_roi_percent'] is None`

### QA-049 — `test_duplicate_benefit_rejected`

Lokacija: `test_project_finance.py:38`. **Svrha i očekivano ponašanje:** Dupli nazivi koristi u scenariju moraju biti odbijeni. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-050 — `test_ranking_is_data_driven_not_fixed`

Lokacija: `test_project_planner.py:7`. **Svrha i očekivano ponašanje:** Rangiranje slijedi unesene faktore, a ne fiksni redoslijed projekata. 

- Očekivanje: `self.assertEqual(r['candidates'][0]['title'], 'Smanjenje škarta')`
- Očekivanje: `self.assertEqual(r['candidates'][0]['score'], 80)`
- Očekivanje: `self.assertEqual(len(r['candidates'][0]['unverified_factors']), 5)`

### QA-051 — `test_no_fabricated_financials_or_approved_baseline`

Lokacija: `test_project_planner.py:12`. **Svrha i očekivano ponašanje:** Deterministički projektni nacrt ne izmišlja finansije ili odobrenu osnovicu. 

- Očekivanje: `self.assertEqual(d['charter']['financial_effects'], [])`
- Očekivanje: `self.assertFalse(d['charter']['baseline_verified'])`
- Očekivanje: `self.assertEqual(d['status'], 'DRAFT_REQUIRES_CONSULTANT_APPROVAL')`

### QA-052 — `test_unrated_candidate_not_selected`

Lokacija: `test_project_planner.py:17`. **Svrha i očekivano ponašanje:** Neocijenjeni kandidat ne smije biti izabran za projektni nacrt. 

- Očekivanje: `self.assertEqual(d['title'], 'Smanjenje škarta')`

### QA-053 — `test_invalid_rating`

Lokacija: `test_project_planner.py:20`. **Svrha i očekivano ponašanje:** Ocjena faktora izvan raspona mora biti odbijena. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-054 — `test_reports_are_real_documents`

Lokacija: `test_project_reports.py:8`. **Svrha i očekivano ponašanje:** Projektni PDF i DOCX moraju biti stvarni dokumenti s očekivanim sadržajem. 

- Očekivanje: `assert word[:2] == b'PK' and pdf[:4] == b'%PDF'`
- Očekivanje: `assert 'METALPRO DEMO' in text and 'Nezavisno verificirano' in text and ('0 KM' in text)`

### QA-055 — `test_no_estimated_values_are_confirmed`

Lokacija: `test_project_reports.py:14`. **Svrha i očekivano ponašanje:** Procijenjeni projektni iznosi ne smiju se prikazati kao potvrđeni efekti. 

- Očekivanje: `assert '0 KM' in all_text and 'Finansijski model nije unesen' in all_text`

### QA-056 — `test_deployment_bundle_contains_all_modules`

Lokacija: `test_release_preflight.py:3`. **Svrha i očekivano ponašanje:** Preflight provjerava prisutnost obaveznih modula u deployment materijalu. 

- Očekivanje: `assert check_bundle() == []`

### QA-057 — `test_runtime_rejects_missing_secrets`

Lokacija: `test_release_preflight.py:6`. **Svrha i očekivano ponašanje:** Runtime preflight odbija nedostajuće sigurnosne postavke. 

- Očekivanje: `assert len(check_runtime()) >= 4`

### QA-058 — `test_runtime_accepts_valid_test_settings`

Lokacija: `test_release_preflight.py:11`. **Svrha i očekivano ponašanje:** Runtime preflight prihvata valjane sintetičke HTTPS postavke. 

- Očekivanje: `assert check_runtime() == []`

### QA-059 — `test_iso_week_validation`

Lokacija: `test_release_week_validation.py:7`. **Svrha i očekivano ponašanje:** Sedmični pregled prihvata samo stvarne ISO sedmice. 

- Očekivanje: `assert ReviewIn(week='2020-W53').week == '2020-W53'`
- Očekivanje: `assert ReviewIn(week='2026-W46').week == '2026-W46'`

### QA-060 — `test_invalid_week_does_not_create_review_or_audit`

Lokacija: `test_release_week_validation.py:19`. **Svrha i očekivano ponašanje:** Neispravna sedmica ne stvara pregled niti audit događaj. 

- Očekivanje: `assert r.status_code == 201, r.text`
- Očekivanje: `assert c.post(base + '/approve-validation', headers=h).status_code == 200`
- Očekivanje: `assert c.put(base + '/charter', json=charter, headers=h).status_code == 200`
- Očekivanje: `assert c.post(base + '/approve-implementation', headers=h).status_code == 200`
- Očekivanje: `assert c.get(base).json()['weekly_reviews'] == []`
- Očekivanje: `assert len(c.get(base + '/audit').json()['events']) == audit_before`
- Očekivanje: `assert c.post(base + '/weekly-reviews', json={'week': '2026-W46'}, headers=h).status_code == 201`
- Očekivanje: `assert response.status_code == 422, (week, response.text)`

### QA-061 — `test_https_target_validation`

Lokacija: `test_remote_acceptance.py:17`. **Svrha i očekivano ponašanje:** Remote acceptance prihvata samo dozvoljen HTTPS osnovni URL. 

- Očekivanje: `assert validate_target('https://test.example.invalid/') == 'https://test.example.invalid'`

### QA-062 — `test_anonymous_acceptance_success`

Lokacija: `test_remote_acceptance.py:22`. **Svrha i očekivano ponašanje:** Mock anonimni HTTPS odgovori prolaze očekivani acceptance ugovor. 

- Očekivanje: `assert all((ok for _, ok, _ in check('https://test.example.invalid', FakeOpener())))`

### QA-063 — `test_anonymous_data_leak_detected`

Lokacija: `test_remote_acceptance.py:25`. **Svrha i očekivano ponašanje:** Remote acceptance otkriva anonimno izlaganje zaštićenog ekrana. 

- Očekivanje: `assert not dict(((path, ok) for path, ok, _ in results))['/projects-ui']`

### QA-064 — `test_anonymous_workspace_leak_detected`

Lokacija: `test_remote_acceptance.py:29`. **Svrha i očekivano ponašanje:** Remote acceptance otkriva anonimno izlaganje workspace API-ja. 

- Očekivanje: `assert not dict(((path, ok) for path, ok, _ in results))['/api/workspace']`

### QA-065 — `test_weekly_ui_uses_forms_not_json_textareas`

Lokacija: `test_weekly_ui.py:6`. **Svrha i očekivano ponašanje:** Sedmični interfejs koristi strukturirane forme umjesto sirovog JSON unosa. 

- Očekivanje: `assert 'id="weekActivityRows"' in html`
- Očekivanje: `assert 'id="weekKpiRows"' in html`
- Očekivanje: `assert 'function weeklyPayload()' in html`
- Očekivanje: `assert 'id="weekActivities"' not in html`
- Očekivanje: `assert 'id="weekKpis"' not in html`

### QA-066 — `test_weekly_data_roundtrip`

Lokacija: `test_weekly_ui.py:13`. **Svrha i očekivano ponašanje:** Sedmični podaci ostaju isti nakon upisa i ponovnog čitanja. 

- Očekivanje: `assert self.client.post(f'/api/v4/projects/{pid}/approve-implementation', headers=self.headers).status_code == 200`
- Očekivanje: `assert self.client.post(f'/api/v4/projects/{pid}/weekly-reviews', json=week, headers=self.headers).status_code == 201`
- Očekivanje: `assert actual['kpi_measurements'][0]['value'] == '82%'`
- Očekivanje: `assert actual['activities'][0]['status'] == 'in_progress'`

### QA-067 — `test_extractor_handles_multiple_scripts_and_rejects_broken_main`

Lokacija: `test_word_qa.py:11`. **Svrha i očekivano ponašanje:** Word extractor obrađuje više script blokova i odbija neispravnu glavnu skriptu. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-068 — `test_twelve_word_reports_and_corruption_checks`

Lokacija: `test_word_qa.py:24`. **Svrha i očekivano ponašanje:** Svih 12 Word dokumenata prolazi strukturu, a oštećenja se detektuju. 

- Očekivanje: `assert '12 DOCX' in generated.stdout`
- Očekivanje: `assert subprocess.run(['node', 'qa_word_reports.js'], cwd=ROOT, env=env, capture_output=True).returncode != 0`
- Očekivanje: `assert subprocess.run([sys.executable, 'qa_word_reports.py'], cwd=ROOT, env=env, capture_output=True).returncode != 0`

### QA-069 — `test_approval_snapshot_survives_future_edit`

Lokacija: `tests/test_approval.py:28`. **Svrha i očekivano ponašanje:** Zaključani snimak odobrenja preživljava buduću promjenu radnog workspacea. 

- Očekivanje: `self.assertEqual(read_approval(self.db, approval['approval_id'])['workspace'], self.first)`

### QA-070 — `test_stale_revision_rejected`

Lokacija: `tests/test_approval.py:33`. **Svrha i očekivano ponašanje:** Odobravanje zastarjele revizije mora biti odbijeno. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-071 — `test_reviewer_required`

Lokacija: `tests/test_approval.py:37`. **Svrha i očekivano ponašanje:** Odobravanje zahtijeva imenovanog konsultanta. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-072 — `test_corrupted_snapshot_rejected`

Lokacija: `tests/test_approval.py:41`. **Svrha i očekivano ponašanje:** Izmijenjen hash ili sadržaj odobrenog snimka mora biti odbijen. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-073 — `test_incomplete_diagnostic_cannot_be_approved`

Lokacija: `tests/test_approval.py:47`. **Svrha i očekivano ponašanje:** Nepotpuna dijagnostika ne smije biti odobrena. 

- Očekivanje: `self.assertEqual(self.db.execute('SELECT COUNT(*) FROM diagnostic_approvals_test').fetchone()[0], 0)`

### QA-074 — `test_warning_cannot_be_approved`

Lokacija: `tests/test_approval.py:54`. **Svrha i očekivano ponašanje:** WARN stanje ne smije dobiti završno odobrenje. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-075 — `test_legacy_table_untouched`

Lokacija: `tests/test_approval.py:63`. **Svrha i očekivano ponašanje:** TEST odobravanje ne mijenja legacy workspace tabelu. 

- Očekivanje: `self.assertIsNone(self.db.execute("SELECT name FROM sqlite_master WHERE name='workspace'").fetchone())`

### QA-076 — `test_immutable_reports_and_backup`

Lokacija: `tests/test_approved_delivery.py:60`. **Svrha i očekivano ponašanje:** Izvještaji ostaju vezani uz odobreni snimak i sačuvani sadržaj baze. 

- Očekivanje: `self.assertEqual(prepare_report_manifest(db, approval, 0, 0)['diagnostic_id'], 'prva')`
- Očekivanje: `self.assertEqual(r.status_code, 200)`
- Očekivanje: `self.assertIn('Za dijagnostiku prva', text)`
- Očekivanje: `self.assertNotIn('Za dijagnostiku druga', text)`
- Očekivanje: `self.assertNotIn('kasnija izmjena', text)`
- Očekivanje: `self.assertEqual('Dokaz F01' in text, view == 'detailed')`
- Očekivanje: `self.assertTrue(r.content.startswith(b'%PDF'))`

### QA-077 — `test_unbound_legacy_approval_requires_review`

Lokacija: `tests/test_approved_delivery.py:86`. **Svrha i očekivano ponašanje:** Staro odobrenje bez veze s dijagnostikom zahtijeva novi pregled. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-078 — `test_export_verify`

Lokacija: `tests/test_backup_snapshot.py:19`. **Svrha i očekivano ponašanje:** TEST snapshot izvoz ima ispravan hash i format. 

- Očekivanje: `self.assertEqual(verify_snapshot(snapshot)['workspace'], self.original)`

### QA-079 — `test_tamper_rejected`

Lokacija: `tests/test_backup_snapshot.py:23`. **Svrha i očekivano ponašanje:** Neovlaštena izmjena TEST snapshot sadržaja mora biti otkrivena. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-080 — `test_confirmation_required`

Lokacija: `tests/test_backup_snapshot.py:29`. **Svrha i očekivano ponašanje:** TEST restore zahtijeva izričitu potvrdu. 

- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['revision'], 1)`

### QA-081 — `test_restore_creates_new_revision`

Lokacija: `tests/test_backup_snapshot.py:35`. **Svrha i očekivano ponašanje:** TEST restore stvara novu radnu reviziju umjesto vraćanja starog broja. 

- Očekivanje: `self.assertEqual(new_rev, 3)`
- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['workspace'], self.original)`

### QA-082 — `test_stale_restore_rejected`

Lokacija: `tests/test_backup_snapshot.py:43`. **Svrha i očekivano ponašanje:** TEST restore sa zastarjelom očekivanom revizijom mora biti odbijen. 

- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['revision'], 2)`

### QA-083 — `test_na_indices_and_empty_dimensions`

Lokacija: `tests/test_package2.py:52`. **Svrha i očekivano ponašanje:** N/P indeksi koriste odgovarajuće nazivnike i None za prazne oblasti. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approval.status_code == 200, approval.text`
- Očekivanje: `assert model['coverage']['applicable'] == sum((r['verification_status'] != 'nije_primjenjivo' for r in d['quality_records']))`
- Očekivanje: `assert (model if code is None else model['dimensions'][code])['index'] == expected`
- Očekivanje: `assert 'N/P' in text and 'QA-konsultant' in text and ('Kompanija ne koristi' in text)`
- Očekivanje: `assert 'Neocjenjivo' in text and '0/100' not in text`

### QA-084 — `test_undocumented_na_blocks`

Lokacija: `tests/test_package2.py:74`. **Svrha i očekivano ponašanje:** Nedokumentovan ili pogrešno popunjen N/P blokira novo odobrenje. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approve(client).status_code == 422`
- Očekivanje: `assert client.get('/api/test/v2/approvals').json() == []`

### QA-085 — `test_applicable_unverified_still_blocks_real`

Lokacija: `tests/test_package2.py:82`. **Svrha i očekivano ponašanje:** Neprovjeren primjenjivi kriterij i dalje blokira stvarni finalni izvještaj. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approve(client).status_code == 422`

### QA-086 — `test_demo_mode_locked_manifest_labels_and_four_formats`

Lokacija: `tests/test_package2.py:96`. **Svrha i očekivano ponašanje:** DEMO režim i oznake ostaju vezani uz manifest i sva četiri formata. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approval.status_code == 200, approval.text`
- Očekivanje: `assert save(client, d, 1).status_code == 200`
- Očekivanje: `assert approve(client, 2).status_code == 422`
- Očekivanje: `assert client.get('/api/test/v2/approvals').json()[0]['report_mode'] == 'demo'`
- Očekivanje: `assert DEMO_LABEL in doc_text(client, aid, 'executive', 'docx', tmp)[0]`
- Očekivanje: `assert a['report_mode'] == manifest['report_mode'] == 'demo'`
- Očekivanje: `assert a['policy_version'] == manifest['policy_version'] == 2`
- Očekivanje: `assert DEMO_LABEL in text and 'nije stvarno' in text`
- Očekivanje: `assert 'Odobrenje ' not in text and '_DEMO_' in r.headers['content-disposition']`
- Očekivanje: `assert DEMO_LABEL in word.sections[0].header.paragraphs[0].text`
- Očekivanje: `assert DEMO_LABEL in word.sections[0].footer.paragraphs[0].text`
- Očekivanje: `assert all((DEMO_LABEL in p for p in pages))`

### QA-087 — `test_demo_cannot_certify_verified_claims_or_skip_data`

Lokacija: `tests/test_package2.py:122`. **Svrha i očekivano ponašanje:** DEMO ne može potvrditi provjerene tvrdnje ili preskočiti podatke. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approve(client).status_code == 422`

### QA-088 — `test_explicit_real_mode_cannot_relabel_simulated_source`

Lokacija: `tests/test_package2.py:132`. **Svrha i očekivano ponašanje:** Izbor real režima ne pretvara simulirane izvorne ulaze u stvarni nalaz. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approve(client).status_code == 422`

### QA-089 — `test_frozen_model_and_collection_survive_later_work_and_restore`

Lokacija: `tests/test_package2.py:138`. **Svrha i očekivano ponašanje:** Zamrznuti model i source bilješke ostaju očuvani nakon daljeg rada i restorea. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert approval.status_code == 200`
- Očekivanje: `assert loaded['guided'] == d['guided'] and loaded['quality_records'][0]['collection'] == d['quality_records'][0]['collection']`
- Očekivanje: `assert save(client, d, 1).status_code == 200`
- Očekivanje: `assert doc_text(client, aid, 'detailed', 'docx', tmp)[0] == before`
- Očekivanje: `assert read_approval(db, aid)['sha256'] == approval.json()['sha256']`

### QA-090 — `test_historical_v1_snapshot_keeps_old_reader`

Lokacija: `tests/test_package2.py:157`. **Svrha i očekivano ponašanje:** Historijski snimak v1 koristi kompatibilni raniji čitač. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert 'historical' in doc_text(client, aid, view, fmt, tmp)[0]`

### QA-091 — `test_working_engine_empty_applicable_is_none`

Lokacija: `tests/test_package2.py:171`. **Svrha i očekivano ponašanje:** Engine vraća None kada nema primjenjivih ocjenjivih kriterija. 

- Očekivanje: `assert result['index'] is None and result['coverage']['applicable'] == 0`
- Očekivanje: `assert all((d['index'] is None for d in result['dimensions'].values()))`

### QA-092 — `test_minimal_justified_na_does_not_require_applicable_evidence_fields`

Lokacija: `tests/test_package2.py:177`. **Svrha i očekivano ponašanje:** Opravdan N/P ne zahtijeva metapodatke dokaza koji važe samo za primjenjivi kriterij. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert r.status_code == 200, r.text`
- Očekivanje: `assert 'N/P' in doc_text(client, r.json()['approval_id'], view, fmt, tmp)[0]`

### QA-093 — `test_malformed_collection_is_rejected_without_losing_workspace`

Lokacija: `tests/test_package2.py:188`. **Svrha i očekivano ponašanje:** Neispravna collection struktura odbija se bez gubitka sačuvanog workspacea. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert save(client, d, 1).status_code == 422`
- Očekivanje: `assert client.get('/api/test/v2/workspace').json() == before`

### QA-094 — `test_inconsistent_snapshot_mode_fails_closed`

Lokacija: `tests/test_package2.py:196`. **Svrha i očekivano ponašanje:** Neusklađen režim zaključanog snimka mora biti odbijen. 

- Očekivanje: `assert save(client, d).status_code == 200`
- Očekivanje: `assert client.get(f'/api/test/v2/approvals/{aid}/executive/pdf').status_code == 422`

### QA-095 — `test_missing_criteria_blocks`

Lokacija: `tests/test_report_gate.py:6`. **Svrha i očekivano ponašanje:** Nedostajući kriteriji blokiraju završni gate. 

- Očekivanje: `self.assertEqual(result['status'], 'BLOCK')`

### QA-096 — `test_revision_mismatch_blocks`

Lokacija: `tests/test_report_gate.py:10`. **Svrha i očekivano ponašanje:** Razlika odobrene i izvještajne revizije blokira gate. 

- Očekivanje: `self.assertIn('Izvještaj nije vezan za odobrenu reviziju', result['issues'])`

### QA-097 — `test_reviewer_missing_blocks`

Lokacija: `tests/test_report_gate.py:14`. **Svrha i očekivano ponašanje:** Nedostajući konsultant blokira gate. 

- Očekivanje: `self.assertIn('Nedostaje odgovorni konsultant', result['issues'])`

### QA-098 — `test_critical_risk_review_blocks`

Lokacija: `tests/test_report_gate.py:18`. **Svrha i očekivano ponašanje:** Nedostajući eksplicitni pregled kritičnog rizika blokira gate. 

- Očekivanje: `self.assertTrue(any(('procjena rizika O14' in x for x in result['issues'])))`

### QA-099 — `test_unverified_financial_claim_blocks`

Lokacija: `tests/test_report_gate.py:23`. **Svrha i očekivano ponašanje:** Neprovjerena finansijska tvrdnja blokira gate. 

- Očekivanje: `self.assertIn('Finansijska korist nije nezavisno potvrđena', result['issues'])`

### QA-100 — `test_missing_evidence_warns_even_if_record_not_blocked`

Lokacija: `tests/test_report_gate.py:29`. **Svrha i očekivano ponašanje:** Nedostajući dokaz daje upozorenje čak i kada pojedinačni zapis nema error. 

- Očekivanje: `self.assertTrue(any(('bez dokaza' in w for w in result['warnings'])))`

### QA-101 — `test_simulated_data_flagged`

Lokacija: `tests/test_report_gate.py:35`. **Svrha i očekivano ponašanje:** Simulirani podaci moraju biti označeni u stvarnom izvještajnom gateu. 

- Očekivanje: `self.assertTrue(any(('simulirane podatke' in w for w in result['warnings'])))`

### QA-102 — `test_invalid_finance_payload_rejected`

Lokacija: `tests/test_report_gate.py:41`. **Svrha i očekivano ponašanje:** Neispravan format finansijskog payload-a mora biti odbijen. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-103 — `test_self_assessment_is_not_clean_pass`

Lokacija: `tests/test_report_gate.py:45`. **Svrha i očekivano ponašanje:** Samoprocjena ne smije dobiti čisti PASS. 

- Očekivanje: `self.assertTrue(any(('samoprocjene' in w for w in result['warnings'])))`

### QA-104 — `test_na_requires_scope_warning`

Lokacija: `tests/test_report_gate.py:50`. **Svrha i očekivano ponašanje:** Historijska policy v1 zadržava upozorenje o N/P obuhvatu. 

- Očekivanje: `self.assertTrue(any(('N/P' in w for w in result['warnings'])))`

### QA-105 — `test_simulated_flag_even_if_status_is_different`

Lokacija: `tests/test_report_gate.py:56`. **Svrha i očekivano ponašanje:** Simulacijska zastavica mora se uočiti i uz drugačiji status zapisa. 

- Očekivanje: `self.assertTrue(any(('simulirane' in w for w in result['warnings'])))`

### QA-106 — `test_missing_quality_records_fail_closed`

Lokacija: `tests/test_report_manifest.py:24`. **Svrha i očekivano ponašanje:** Manifest se ne pravi kada nedostaju quality_records. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-107 — `test_blocked_quality_gate_refuses_manifest`

Lokacija: `tests/test_report_manifest.py:28`. **Svrha i očekivano ponašanje:** BLOCK gate ne smije proizvesti izvještajni manifest. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-108 — `test_warning_refuses_manifest`

Lokacija: `tests/test_report_manifest.py:32`. **Svrha i očekivano ponašanje:** WARN gate ne smije proizvesti izvještajni manifest. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-109 — `test_pass_produces_snapshot_bound_manifest`

Lokacija: `tests/test_report_manifest.py:39`. **Svrha i očekivano ponašanje:** PASS proizvodi manifest vezan uz odgovarajući odobreni snimak. 

- Očekivanje: `self.assertEqual(result['status'], 'READY_FOR_TEST_RENDER')`
- Očekivanje: `self.assertEqual(result['workspace_revision'], 1)`
- Očekivanje: `self.assertEqual(len(result['snapshot_sha256']), 64)`

### QA-110 — `test_placeholder_in_all_seven_fields_cannot_be_approved`

Lokacija: `tests/test_review_validation.py:28`. **Svrha i očekivano ponašanje:** Zamjenski tekst u svih sedam review polja ne smije dobiti novo odobrenje. 

- Očekivanje: `assert response.status_code == 422`
- Očekivanje: `assert db.execute('SELECT COUNT(*) FROM diagnostic_approvals_test').fetchone()[0] == 0`

### QA-111 — `test_each_field_is_independently_required`

Lokacija: `tests/test_review_validation.py:38`. **Svrha i očekivano ponašanje:** Svako review polje zasebno mora ispuniti svoje tehničke uslove. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-112 — `test_valid_bosnian_review_approves_and_downloads_four_formats`

Lokacija: `tests/test_review_validation.py:44`. **Svrha i očekivano ponašanje:** Valjan bosanski pregled dobija odobrenje i sva četiri izvještaja. 

- Očekivanje: `assert r.status_code == 200, r.text`
- Očekivanje: `assert doc.status_code == 200`

### QA-113 — `test_historical_short_approved_content_remains_readable`

Lokacija: `tests/test_review_validation.py:53`. **Svrha i očekivano ponašanje:** Historijski odobren kratak review ostaje čitljiv. 

- Očekivanje: `assert save_and_approve(client, d).status_code == 422`
- Očekivanje: `assert client.get(f"/api/test/v2/approvals/{approval['approval_id']}/{view}/{fmt}").status_code == 200`

### QA-114 — `test_malformed_review_is_a_validation_error`

Lokacija: `tests/test_review_validation.py:66`. **Svrha i očekivano ponašanje:** Neispravan oblik review objekta vraća validacijsku grešku. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-115 — `test_initial_revision`

Lokacija: `tests/test_sync_guard.py:19`. **Svrha i očekivano ponašanje:** Prazni TEST store ima početnu reviziju nula. 

- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['revision'], 0)`

### QA-116 — `test_first_save`

Lokacija: `tests/test_sync_guard.py:22`. **Svrha i očekivano ponašanje:** Prvi TEST upis stvara reviziju jedan. 

- Očekivanje: `self.assertEqual(save_test_workspace(self.db, self.workspace, 0), 1)`
- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['workspace'], self.workspace)`

### QA-117 — `test_stale_save_rejected_and_data_preserved`

Lokacija: `tests/test_sync_guard.py:26`. **Svrha i očekivano ponašanje:** Zastarjeli TEST upis odbija se bez promjene postojećih podataka. 

- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['workspace'], newer)`
- Očekivanje: `self.assertEqual(read_test_workspace(self.db)['revision'], 2)`

### QA-118 — `test_invalid_revision`

Lokacija: `tests/test_sync_guard.py:35`. **Svrha i očekivano ponašanje:** Neispravan tip ili vrijednost revizije mora biti odbijen. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-119 — `test_invalid_workspace`

Lokacija: `tests/test_sync_guard.py:39`. **Svrha i očekivano ponašanje:** Neispravan oblik workspacea mora biti odbijen. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-120 — `test_no_changes_to_legacy_table`

Lokacija: `tests/test_sync_guard.py:43`. **Svrha i očekivano ponašanje:** TEST workspace čuvanje ne mijenja legacy tabelu. 

- Očekivanje: `self.assertEqual(self.db.execute("SELECT name FROM sqlite_master WHERE name='workspace'").fetchone(), None)`

### QA-121 — `test_missing_security_callbacks_rejected`

Lokacija: `tests/test_workspace_api.py:30`. **Svrha i očekivano ponašanje:** TEST router ne može biti kreiran bez eksplicitnih sigurnosnih callbackova. 

- Metoda delegira provjeru helperu/context manageru; tačna očekivanja su u izvornom tijelu. Nema zasebnog izmišljenog pass kriterija.

### QA-122 — `test_authentication_required`

Lokacija: `tests/test_workspace_api.py:34`. **Svrha i očekivano ponašanje:** TEST API zahtijeva autentifikaciju. 

- Očekivanje: `self.assertEqual(self.client.get('/api/test/v2/workspace').status_code, 401)`
- Očekivanje: `self.assertEqual(self.client.put('/api/test/v2/workspace', json={'workspace': self.data, 'expected_revision': 0}).status_code, 401)`

### QA-123 — `test_write_origin_required`

Lokacija: `tests/test_workspace_api.py:41`. **Svrha i očekivano ponašanje:** TEST API upis zahtijeva valjano porijeklo zahtjeva. 

- Očekivanje: `self.assertEqual(response.status_code, 403)`

### QA-124 — `test_conflict_returns_409_without_overwrite`

Lokacija: `tests/test_workspace_api.py:48`. **Svrha i očekivano ponašanje:** Konflikt revizije vraća 409 bez prepisivanja sačuvanog stanja. 

- Očekivanje: `self.assertEqual(first.status_code, 200)`
- Očekivanje: `self.assertEqual(first.json()['revision'], 1)`
- Očekivanje: `self.assertEqual(second.status_code, 200)`
- Očekivanje: `self.assertEqual(stale.status_code, 409)`
- Očekivanje: `self.assertEqual(stale.json()['detail']['current_revision'], 2)`
- Očekivanje: `self.assertEqual(self.client.get(url).json()['workspace'], newer)`

### QA-125 — `test_boolean_revision_rejected`

Lokacija: `tests/test_workspace_api.py:61`. **Svrha i očekivano ponašanje:** Boolean vrijednost ne smije se prihvatiti kao integer revizija. 

- Očekivanje: `self.assertEqual(response.status_code, 422)`

## Svi 168 prethodno izvršeni testni slučajevi

Ova lista je preuzeta iz ranijeg pytest-release.xml. Nema novog izvršavanja; pojedinačni pass vezan je samo za tu seriju i sintetički runtime. Neki vremenski redovi su vrlo kratki jer su unit provjere.

| Slučaj | Klasa/modul | Naziv s parametrima | Prethodni rezultat |
| --- | --- | --- | --- |
| RUN-001 | test_actual_effect_idempotency | test_4000_twice_is_one_effect_and_one_audit | passed |
| RUN-002 | test_actual_effect_idempotency | test_simultaneous_retries_create_exactly_one_row[None] | passed |
| RUN-003 | test_actual_effect_idempotency | test_simultaneous_retries_create_exactly_one_row[racun-1] | passed |
| RUN-004 | test_actual_effect_idempotency | test_distinct_events_and_changed_evidence_are_preserved | passed |
| RUN-005 | test_actual_effect_idempotency | test_key_cannot_be_reused_for_changed_content | passed |
| RUN-006 | test_actual_effect_idempotency | test_key_is_scoped_to_project | passed |
| RUN-007 | test_actual_effect_idempotency | test_existing_legacy_rows_are_not_modified_or_merged | passed |
| RUN-008 | test_actual_effect_idempotency | test_failed_audit_rolls_back_effect_and_allows_retry | passed |
| RUN-009 | test_actual_effect_idempotency | test_invalid_payload_and_key_are_rejected_without_writes | passed |
| RUN-010 | test_backup_restore.BackupRestoreTests | test_corrupted_source_rejected | passed |
| RUN-011 | test_backup_restore.BackupRestoreTests | test_live_wal_backup_restore_and_no_overwrite | passed |
| RUN-012 | test_backup_restore.BackupRestoreTests | test_missing_source_rejected | passed |
| RUN-013 | test_browser_readiness | test_ui_auth_navigation_and_assets | passed |
| RUN-014 | test_dashboard | test_dashboard_route_and_page | passed |
| RUN-015 | test_dashboard | test_dashboard_no_aggregated_financial_amounts | passed |
| RUN-016 | test_data_quality_gate.TestQualityGate | test_benefit_requires_basis | passed |
| RUN-017 | test_data_quality_gate.TestQualityGate | test_duplicate | passed |
| RUN-018 | test_data_quality_gate.TestQualityGate | test_invalid_ratio | passed |
| RUN-019 | test_data_quality_gate.TestQualityGate | test_na_approval | passed |
| RUN-020 | test_data_quality_gate.TestQualityGate | test_simulated_cannot_verify | passed |
| RUN-021 | test_data_quality_gate.TestQualityGate | test_simulation_labeled | passed |
| RUN-022 | test_data_quality_gate.TestQualityGate | test_unknown_not_zero | passed |
| RUN-023 | test_financial_audit.TestProjectExecution | test_auth_origin_and_gate | passed |
| RUN-024 | test_financial_audit.TestProjectExecution | test_protected_without_login | passed |
| RUN-025 | test_financial_audit | test_financial_and_effect_audit | passed |
| RUN-026 | test_http_release_smoke | test_http_smoke_script_is_bundled | passed |
| RUN-027 | test_integration.TestMevan | test_01_protected | passed |
| RUN-028 | test_integration.TestMevan | test_02_login_and_persistence | passed |
| RUN-029 | test_integration.TestMevan | test_02 b_backup_restore_and_audit | passed |
| RUN-030 | test_integration.TestMevan | test_03_ai_without_key_and_logout | passed |
| RUN-031 | test_metalpro_demo | test_61_criteria_and_finance_separation | passed |
| RUN-032 | test_metalpro_demo | test_metalpro_full_offline_workflow | passed |
| RUN-033 | test_package 2_project | test_demo_project_cannot_be_relabelled_or_implemented | passed |
| RUN-034 | test_project_actuals | test_independent_verification_not_claimed | passed |
| RUN-035 | test_project_actuals | test_evidence_required | passed |
| RUN-036 | test_project_actuals | test_pending_not_confirmed | passed |
| RUN-037 | test_project_actuals | test_confirmed_separates_working_capital | passed |
| RUN-038 | test_project_ai_pack.TestAIProjectPack | test_reject_extra_financial_claims | passed |
| RUN-039 | test_project_ai_pack.TestAIProjectPack | test_reject_fabricated_baseline | passed |
| RUN-040 | test_project_ai_pack.TestAIProjectPack | test_selects_ranking_not_fixed_project | passed |
| RUN-041 | test_project_ai_pack.TestAIProjectPack | test_valid_ai_pack_unapproved | passed |
| RUN-042 | test_project_audit.TestProjectExecution | test_auth_origin_and_gate | passed |
| RUN-043 | test_project_audit.TestProjectExecution | test_protected_without_login | passed |
| RUN-044 | test_project_audit | test_project_audit_history | passed |
| RUN-045 | test_project_candidates.TestCandidates | test_empty_analysis | passed |
| RUN-046 | test_project_candidates.TestCandidates | test_no_invented_financial_values | passed |
| RUN-047 | test_project_execution.TestProjectExecution | test_auth_origin_and_gate | passed |
| RUN-048 | test_project_execution.TestProjectExecution | test_protected_without_login | passed |
| RUN-049 | test_project_finance | test_financial_separation | passed |
| RUN-050 | test_project_finance | test_missing_scenario_rejected | passed |
| RUN-051 | test_project_finance | test_unverified_claim_cannot_be_confirmed | passed |
| RUN-052 | test_project_finance | test_no_payback_on_negative_net | passed |
| RUN-053 | test_project_finance | test_no_roi_when_no_investment | passed |
| RUN-054 | test_project_finance | test_duplicate_benefit_rejected | passed |
| RUN-055 | test_project_planner.TestPlanner | test_invalid_rating | passed |
| RUN-056 | test_project_planner.TestPlanner | test_no_fabricated_financials_or_approved_baseline | passed |
| RUN-057 | test_project_planner.TestPlanner | test_ranking_is_data_driven_not_fixed | passed |
| RUN-058 | test_project_planner.TestPlanner | test_unrated_candidate_not_selected | passed |
| RUN-059 | test_project_reports | test_reports_are_real_documents | passed |
| RUN-060 | test_project_reports | test_no_estimated_values_are_confirmed | passed |
| RUN-061 | test_release_preflight | test_deployment_bundle_contains_all_modules | passed |
| RUN-062 | test_release_preflight | test_runtime_rejects_missing_secrets | passed |
| RUN-063 | test_release_preflight | test_runtime_accepts_valid_test_settings | passed |
| RUN-064 | test_release_week_validation.TestProjectExecution | test_auth_origin_and_gate | passed |
| RUN-065 | test_release_week_validation.TestProjectExecution | test_protected_without_login | passed |
| RUN-066 | test_release_week_validation | test_iso_week_validation | passed |
| RUN-067 | test_release_week_validation | test_invalid_week_does_not_create_review_or_audit | passed |
| RUN-068 | test_remote_acceptance | test_https_target_validation | passed |
| RUN-069 | test_remote_acceptance | test_anonymous_acceptance_success | passed |
| RUN-070 | test_remote_acceptance | test_anonymous_data_leak_detected | passed |
| RUN-071 | test_remote_acceptance | test_anonymous_workspace_leak_detected | passed |
| RUN-072 | test_weekly_ui.TestProjectExecution | test_auth_origin_and_gate | passed |
| RUN-073 | test_weekly_ui.TestProjectExecution | test_protected_without_login | passed |
| RUN-074 | test_weekly_ui.TestWeeklyForms | test_auth_origin_and_gate | passed |
| RUN-075 | test_weekly_ui.TestWeeklyForms | test_protected_without_login | passed |
| RUN-076 | test_weekly_ui.TestWeeklyForms | test_weekly_data_roundtrip | passed |
| RUN-077 | test_weekly_ui.TestWeeklyForms | test_weekly_ui_uses_forms_not_json_textareas | passed |
| RUN-078 | test_word_qa | test_extractor_handles_multiple_scripts_and_rejects_broken_main | passed |
| RUN-079 | test_word_qa | test_twelve_word_reports_and_corruption_checks | passed |
| RUN-080 | tests.test_approval.ApprovalTests | test_approval_snapshot_survives_future_edit | passed |
| RUN-081 | tests.test_approval.ApprovalTests | test_corrupted_snapshot_rejected | passed |
| RUN-082 | tests.test_approval.ApprovalTests | test_incomplete_diagnostic_cannot_be_approved | passed |
| RUN-083 | tests.test_approval.ApprovalTests | test_legacy_table_untouched | passed |
| RUN-084 | tests.test_approval.ApprovalTests | test_reviewer_required | passed |
| RUN-085 | tests.test_approval.ApprovalTests | test_stale_revision_rejected | passed |
| RUN-086 | tests.test_approval.ApprovalTests | test_warning_cannot_be_approved | passed |
| RUN-087 | tests.test_approved_delivery.ApprovedDelivery | test_immutable_reports_and_backup | passed |
| RUN-088 | tests.test_approved_delivery.ApprovedDelivery | test_unbound_legacy_approval_requires_review | passed |
| RUN-089 | tests.test_backup_snapshot.BackupTests | test_confirmation_required | passed |
| RUN-090 | tests.test_backup_snapshot.BackupTests | test_export_verify | passed |
| RUN-091 | tests.test_backup_snapshot.BackupTests | test_restore_creates_new_revision | passed |
| RUN-092 | tests.test_backup_snapshot.BackupTests | test_stale_restore_rejected | passed |
| RUN-093 | tests.test_backup_snapshot.BackupTests | test_tamper_rejected | passed |
| RUN-094 | tests.test_package 2 | test_na_indices_and_empty_dimensions[F] | passed |
| RUN-095 | tests.test_package 2 | test_na_indices_and_empty_dimensions[O] | passed |
| RUN-096 | tests.test_package 2 | test_na_indices_and_empty_dimensions[P] | passed |
| RUN-097 | tests.test_package 2 | test_na_indices_and_empty_dimensions[L] | passed |
| RUN-098 | tests.test_package 2 | test_na_indices_and_empty_dimensions[M] | passed |
| RUN-099 | tests.test_package 2 | test_na_indices_and_empty_dimensions[mixed] | passed |
| RUN-100 | tests.test_package 2 | test_na_indices_and_empty_dimensions[all] | passed |
| RUN-101 | tests.test_package 2 | test_undocumented_na_blocks[change 0] | passed |
| RUN-102 | tests.test_package 2 | test_undocumented_na_blocks[change 1] | passed |
| RUN-103 | tests.test_package 2 | test_undocumented_na_blocks[change 2] | passed |
| RUN-104 | tests.test_package 2 | test_undocumented_na_blocks[change 3] | passed |
| RUN-105 | tests.test_package 2 | test_undocumented_na_blocks[change 4] | passed |
| RUN-106 | tests.test_package 2 | test_applicable_unverified_still_blocks_real[nema_podataka] | passed |
| RUN-107 | tests.test_package 2 | test_applicable_unverified_still_blocks_real[samoprocjena] | passed |
| RUN-108 | tests.test_package 2 | test_applicable_unverified_still_blocks_real[dokumentovano_neprovjereno] | passed |
| RUN-109 | tests.test_package 2 | test_applicable_unverified_still_blocks_real[simulacija] | passed |
| RUN-110 | tests.test_package 2 | test_demo_mode_locked_manifest_labels_and_four_formats | passed |
| RUN-111 | tests.test_package 2 | test_demo_cannot_certify_verified_claims_or_skip_data[mixed_verified] | passed |
| RUN-112 | tests.test_package 2 | test_demo_cannot_certify_verified_claims_or_skip_data[missing_evidence] | passed |
| RUN-113 | tests.test_package 2 | test_demo_cannot_certify_verified_claims_or_skip_data[claim] | passed |
| RUN-114 | tests.test_package 2 | test_demo_cannot_certify_verified_claims_or_skip_data[missing_score] | passed |
| RUN-115 | tests.test_package 2 | test_explicit_real_mode_cannot_relabel_simulated_source | passed |
| RUN-116 | tests.test_package 2 | test_frozen_model_and_collection_survive_later_work_and_restore | passed |
| RUN-117 | tests.test_package 2 | test_historical_v 1_snapshot_keeps_old_reader | passed |
| RUN-118 | tests.test_package 2 | test_working_engine_empty_applicable_is_none | passed |
| RUN-119 | tests.test_package 2 | test_minimal_justified_na_does_not_require_applicable_evidence_fields | passed |
| RUN-120 | tests.test_package 2 | test_malformed_collection_is_rejected_without_losing_workspace[None] | passed |
| RUN-121 | tests.test_package 2 | test_malformed_collection_is_rejected_without_losing_workspace[value 1] | passed |
| RUN-122 | tests.test_package 2 | test_malformed_collection_is_rejected_without_losing_workspace[value 2] | passed |
| RUN-123 | tests.test_package 2 | test_malformed_collection_is_rejected_without_losing_workspace[value 3] | passed |
| RUN-124 | tests.test_package 2 | test_inconsistent_snapshot_mode_fails_closed | passed |
| RUN-125 | tests.test_report_gate.ReportGateTests | test_critical_risk_review_blocks | passed |
| RUN-126 | tests.test_report_gate.ReportGateTests | test_invalid_finance_payload_rejected | passed |
| RUN-127 | tests.test_report_gate.ReportGateTests | test_missing_criteria_blocks | passed |
| RUN-128 | tests.test_report_gate.ReportGateTests | test_missing_evidence_warns_even_if_record_not_blocked | passed |
| RUN-129 | tests.test_report_gate.ReportGateTests | test_na_requires_scope_warning | passed |
| RUN-130 | tests.test_report_gate.ReportGateTests | test_reviewer_missing_blocks | passed |
| RUN-131 | tests.test_report_gate.ReportGateTests | test_revision_mismatch_blocks | passed |
| RUN-132 | tests.test_report_gate.ReportGateTests | test_self_assessment_is_not_clean_pass | passed |
| RUN-133 | tests.test_report_gate.ReportGateTests | test_simulated_data_flagged | passed |
| RUN-134 | tests.test_report_gate.ReportGateTests | test_simulated_flag_even_if_status_is_different | passed |
| RUN-135 | tests.test_report_gate.ReportGateTests | test_unverified_financial_claim_blocks | passed |
| RUN-136 | tests.test_report_manifest.ReportManifestTests | test_blocked_quality_gate_refuses_manifest | passed |
| RUN-137 | tests.test_report_manifest.ReportManifestTests | test_missing_quality_records_fail_closed | passed |
| RUN-138 | tests.test_report_manifest.ReportManifestTests | test_pass_produces_snapshot_bound_manifest | passed |
| RUN-139 | tests.test_report_manifest.ReportManifestTests | test_warning_refuses_manifest | passed |
| RUN-140 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[] | passed |
| RUN-141 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[   ] | passed |
| RUN-142 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[x] | passed |
| RUN-143 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[TODO] | passed |
| RUN-144 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[value 4] | passed |
| RUN-145 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[value 5] | passed |
| RUN-146 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[value 6] | passed |
| RUN-147 | tests.test_review_validation | test_placeholder_in_all_seven_fields_cannot_be_approved[value 7] | passed |
| RUN-148 | tests.test_review_validation | test_each_field_is_independently_required[summary] | passed |
| RUN-149 | tests.test_review_validation | test_each_field_is_independently_required[priority 1] | passed |
| RUN-150 | tests.test_review_validation | test_each_field_is_independently_required[priority 2] | passed |
| RUN-151 | tests.test_review_validation | test_each_field_is_independently_required[priority 3] | passed |
| RUN-152 | tests.test_review_validation | test_each_field_is_independently_required[month 1] | passed |
| RUN-153 | tests.test_review_validation | test_each_field_is_independently_required[month 2] | passed |
| RUN-154 | tests.test_review_validation | test_each_field_is_independently_required[month 3] | passed |
| RUN-155 | tests.test_review_validation | test_valid_bosnian_review_approves_and_downloads_four_formats | passed |
| RUN-156 | tests.test_review_validation | test_historical_short_approved_content_remains_readable | passed |
| RUN-157 | tests.test_review_validation | test_malformed_review_is_a_validation_error | passed |
| RUN-158 | tests.test_sync_guard.SyncGuardTests | test_first_save | passed |
| RUN-159 | tests.test_sync_guard.SyncGuardTests | test_initial_revision | passed |
| RUN-160 | tests.test_sync_guard.SyncGuardTests | test_invalid_revision | passed |
| RUN-161 | tests.test_sync_guard.SyncGuardTests | test_invalid_workspace | passed |
| RUN-162 | tests.test_sync_guard.SyncGuardTests | test_no_changes_to_legacy_table | passed |
| RUN-163 | tests.test_sync_guard.SyncGuardTests | test_stale_save_rejected_and_data_preserved | passed |
| RUN-164 | tests.test_workspace_api.TestWorkspaceAPI | test_authentication_required | passed |
| RUN-165 | tests.test_workspace_api.TestWorkspaceAPI | test_boolean_revision_rejected | passed |
| RUN-166 | tests.test_workspace_api.TestWorkspaceAPI | test_conflict_returns_409_without_overwrite | passed |
| RUN-167 | tests.test_workspace_api.TestWorkspaceAPI | test_missing_security_callbacks_rejected | passed |
| RUN-168 | tests.test_workspace_api.TestWorkspaceAPI | test_write_origin_required | passed |

## Browser i Word provjere izvan pytest liste

`browser_smoke.py` provjerava stariji osnovni mobilni tok i položaj backup alata. Ne treba ga poistovjećivati s kasnijim završnim approval testom.

`browser_approved_smoke.py:1` otvara prijavu, provjerava sedam polja konsultantskog pregleda i preuzima četiri izvještaja. Učitava rangiranje C1 81 / C3 72 / C2 67, odbija zastarjelu reviziju i potvrđuje da ponovljeni zahtjev za 4.000 KM ne duplira efekat. Zaseban događaj ostaje dozvoljen.

`browser_package2.py:1` vraća samo sintetički METALPRO primjer i eksplicitno bira DEMO. Unosi tri vrste bilješki, sprema ih i osvježava ekran, potvrđuje N/P prijavljenim konsultantom te povezuje drugi prioritet s projektnim nacrtom i planom. Provjerava četiri označena izvoza, pokušaj promjene režima kroz URL, povratak na glavni ekran i stare print/Word nacrte. Postojeći projekat drugog režima ne smije biti povezan. Obje skripte mijenjaju podatke i smiju se koristiti samo na izolovanom sintetičkom serveru.

`qa_word_reports.js:1` pronalazi tačno jednu glavnu skriptu s funkcijom exportDOCX i kompajlira je cijelu. U VM-u zamjenjuje DOM, storage i fetch testnim objektima. Generiše šest obuhvata puta dva prikaza, ukupno 12 DOCX datoteka. Odbija odredište koje već sadrži Word izvještaje kako ne bi prepisao stare rezultate.

`qa_word_reports.py:1` provjerava ZIP integritet, parsiranje XML-a i osnovni sadržaj svih 12 dokumenata prema stvarnim provjerama u skripti. To nije vizuelni prikaz u Microsoft Wordu ili LibreOffice-u.

`http_release_smoke.py:1` pokreće zaseban lokalni server i privremenu bazu, a zatim provjerava prijavu, sesiju, zaštićene stranice i workspace API. `remote_acceptance.py:1` provjerava samo anonimni HTTPS pristup izričito odobrenoj testnoj instanci. Ne provjerava prijavljeni tok, AI, bazu ili Docker. `release_preflight.py:1` statički provjerava paket, Docker/Compose i opcionalno osnovne runtime postavke; ne vrši deploy.

## Ručni scenariji i status očekivanja

| ID | Scenario i ulaz | Očekivani rezultat | Stanje dokaza |
|---|---|---|---|
| MAN-01 | Nova sintetička dijagnostika sa svih 61 primjenjivim kriterijem. | Indeksi i pokrivenost odgovaraju unosima; finalni gate nema nepoznatih stavki. | Postoje automatizovani dokazi. Stručni terenski pilot nije potvrđen. |
| MAN-02 | Jedan opravdan N/P, svaki isključen modul i potpuno N/P skup. | Nazivnik se smanjuje; prazni indeksi ostaju None, a razlog i konsultant su u oba prikaza. | Automatizovano; reprezentativni PDF je vizuelno pregledan. |
| MAN-03 | N/P bez razloga/potvrde ili primjenjivi kriterij bez dokaza. | Novo odobrenje se odbija, uključujući WARN koji ne prolazi finalni gate. | Automatizovano. |
| MAN-04 | DEMO snimak se preuzima s parametrom mode=real u svakom formatu. | Oznaka ostaje; dokument ne postaje stvarno odobren nalaz. | Automatizovano i pregledani PDF uzorci. |
| MAN-05 | Povratak, osvježavanje i promjena izvornih ocjena. | Bilješke ostaju; promijenjeni ulaz zahtijeva novi pregled i ne prepisuje stare snimke. | Sintetički mobilni tok; potpuni stres više kartica nije potvrđen. |
| MAN-06 | Istovremeni retry efekta, novi ključ i neuspješan audit. | Isti događaj je jedan zapis, drugi legitimni događaj je dozvoljen, a rollback je potpun. | Automatizovano na SQLite-u. |
| MAN-07 | Otvaranje rubnih DOCX izvještaja u Wordu/LibreOffice-u. | Paginacija, zaglavlje, podnožje i tekst su čitljivi. | Vizuelni render nije potvrđen. |
| MAN-08 | Stvarni AI odgovor na sintetičke ulaze i pokušaj prompt injectiona. | AI ne izmišlja činjenice, ne mijenja facts i ne daje odobrenje. | Stvarni AI nije testiran; mock odgovor nije isti dokaz. |
| MAN-09 | Render TLS, trajni volumen, restart i restore. | Podaci ostaju sačuvani i verzija je nedvosmislena. | Nije provjereno ovdje. Preneseni dashboard status nije ovaj test. |
| MAN-10 | Opcionalni PG: CAS, konkurentnost i backup. | Zastarjeli upis je odbijen, a stvarna šema i obuhvat kopije su poznati. | Udaljeni PG nije provjeren; RLS nije implementiran u kodu. |
| MAN-11 | Pristup druge kompanije kao drugog korisnika. | Zahtijeva budući model izolacije i prava. | Nema implementiranog multiuser ACL-a; nije passed. |
| MAN-12 | Registracija, billing, PDV, paketi, kupci ili artikli. | N/A za trenutni proizvod. | Te funkcije nisu implementirane. |
| MAN-13 | Stored XSS, SQL injection i potpuni CSRF pregled. | Nema izvršavanja nepouzdanog sadržaja ili neautorizovanog pristupa. | Postoje negativni unit testovi, ali nema potpunog pentesta. |
| MAN-14 | Generalna proba PIT demonstracije 3–4.12.2026, uključujući rezervne izvoze. | Cijeli odobreni demo tok radi u planiranom okruženju. | Lokalni tok postoji; svi vanjski faktori i proba nisu potvrđeni. |

## Kako nastaviti QA bez uništavanja dokaza

Koristiti novu sintetičku privremena baza i novi izlazni direktorij, ukloniti stvarni OPENAI ključ/PG URL iz testnog procesa, ne dirati stare logove. Pokrenuti relevantne nove regresije tek nakon konkretne promjene; uspješne testove ne ponavljati samo radi dokumentacije. Instalacijske komande i CI tačan opseg su u [infrastrukturi](INFRASTRUCTURE_AND_DEPLOYMENT.md). Novi runner ne smije poistovjetiti 136 prolaza prvog CI runa sa 168 lokalnih prolaza drugog paketa.
