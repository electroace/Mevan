> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: potpuna vidljiva metodologija, poslovni izuzeci i 61 kriterij.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — poslovna logika i metodologija

## Akteri, identitet i poslovni objekti

Jedan administrator/konsultant definisan je env-om, ne redom u users tabeli. Svi prijavljeni zahtjevi imaju ista prava nad istom instancom. Kompanije i dijagnostike su JSON objekti; njihov ID ne predstavlja tenant autorizaciju. Nema dodijeljenih korisnika po kompaniji. Broj kompanija u workspace validaciji je 1–100, dijagnostika najviše 100 po kompaniji; to je tehnički limit payload-a, ne plaćeni paket. Admin e-mail i lozinka postavljaju se na serveru, bez registracije. Više o prijavi u [sigurnosti](SECURITY.md).

Dokument je izvještaj/nacrt, ne račun: zaključana dijagnostika dobija SQLite AUTOINCREMENT approval_id, reviziju, trajni diagnostic_id, reviewer_id, vrijeme i SHA-256. Projekti, sedmični pregledi, audit i efekti koriste UUID; efekti imaju deterministički UUIDv5 za retry. Kompanijski/dijagnostički browser ID može nastati iz Date.now; nema centralne poslovne numeracije ili garancije jedinstvenosti tog browser identifikatora.

## Poslovne funkcije koje ne postoje

Ovo nije fakturisanje ili generički SaaS. Nema registracije, verifikacije e-maila, resetovanja lozinke, pozivnica, korisničke tabele, paketa besplatno/plaćeno, pretplata, kartičnog plaćanja, billing portala, cijena/licenci, PDV obračuna, računa/predračuna, kupaca, artikala ili cjenovnika. Pominjanje kupca/proizvoda u pitanju F02 nije CRM/skladišna funkcija. KM je jedinica finansijskih procjena i evidentiranih efekata, nije cijena softvera. Nema automatizovanih e-mailova, Cloudflare/Supabase autentifikacije ili RLS-a. Odgovarajući testovi tih nepostojećih tokova su N/A, a ne „passed”. Nema pretpostavljene zakonske formule PDV ili numeracije računa.

## Skala i izračun zrelosti

`diagnostic_engine.py:5` definiše F12/O15/P12/L10/M12. Ocjena je cijeli broj 0–5; bool nije validna gate ocjena. Opća UI skala nalazi se u `index.html:22`. Tačan vidljivi tekst je: 0 — Proces ne postoji ili se ne provodi; 1 — Povremena, neformalna praksa; 2 — Djelimično uvedeno, bez dosljednog praćenja; 3 — Definisan proces koji se redovno provodi; 4 — Proces se mjeri, analizira i koriguje; 5 — Standardizovan proces s dokazanim kontinuiranim unapređenjem. To nije 366 kriterijskih ankera.

Za dokumentovane ocjene u skupu S, **indeks = round(20 × sum(ocjene)/len(S), 1)**. Modul ima isti račun nad vlastitim kriterijima. Ukupni indeks je prosjek pojedinačnih kriterija, a ne neponderisani prosjek pet modularnih indeksa. Nema posebnih težina po kriteriju; jednak doprinos u skupu, odnosno 20/N po jedinici ocjene. Moduli zato implicitno doprinose prema broju uključenih kriterija. N/P (`applicable='no'`) se izuzima prije brojača i sume.

Deterministički engine računa samo `proof='confirmed'`, cijelu konačnu ocjenu i neprazan tekst evidence. Njegovo polje `verified` je historijski naziv za popunjenu samoprocjenu, **ne nezavisnu verifikaciju**: `independently_verified_criteria=0` i izričita upozorenja ostaju. U radnom nacrtu primjenjivi, ali nedokumentovani kriteriji ostaju u coverage.applicable i unverified, dok indeks računa dokumentovani podskup. Finalni stvarni gate zahtijeva sve primjenjive provjerene zapise; zato je tamo nazivnik svih primjenjivih kriterija. Prazan ocjenjivi skup daje None/„Neocjenjivo”, ne 0/100.

Primjer: tri primjenjive dokumentovane ocjene 2, 3, 4 daju 60.0. Ako je treći kriterij opravdan N/P, preostale 2, 3 daju 50.0; N/P nije nula koja bi dala 33.3. Modul A: 2 kriterija po 5 =100; modul B: 1 kriterij 0 =0; ukupno 66.7, ne 50.0. Za potpuno N/P skup: coverage.applicable=0, indeks i svih pet modularnih indeksa=None; radar izostavljen s objašnjenjem.

Izvorni METALPRO sintetički uzorak daje ukupno 36.4, F38.3/O34.7/P35.0/L42.0/M33.3 (`test_metalpro_demo.py:8`). Mobilni paket 2 slučaj pretvara F01 u N/P: primjenjivo 60/61, F36.4 i ukupno 36.0; ostali moduli ostaju isti. Različiti ulazi nisu regresija istog primjenjivog slučaja.

## N/P, dokazni statusi i finalni gate

`data_quality_gate.py:8` validira N/P razlog: string, normalizovan whitespace, najmanje 20 znakova, četiri slovne riječi, najmanje tri različite; skup samo test/razlog/x/todo/tekst/naknadno nije dovoljan. `na_approved_by` mora biti string dužine>=2; score=None. Primjer: „Kompanija ne koristi ovaj proces u dokumentovanom obuhvatu dijagnostike.” uz „QA-konsultant” prolazi tehničku potpunost. „x” ili „test test test…” ne prolazi. UI ima potvrdu identitetom prijavljenog konsultanta; API ne dokazuje identitet slobodno unesenog imena posebnim potpisom. Opravdanost ostaje stručna odgovornost.

Statusi su `nema_podataka`, `nije_primjenjivo`, `samoprocjena`, `dokumentovano_neprovjereno`, `provjereno`, `simulacija`. Nepoznato ima praznu ocjenu; numerička nula znači procijenjeno odsustvo procesa. Provjeren status zahtijeva assessor_id, evidence_reference, source_id, reference_period_start/end, assessment_version, timestamp, verification_audit_ref. Provjera ne otvara stvarni dokument. Datumi perioda se porede kao stringovi; potpuna kalendarska validacija tu nije implementirana.

Simulirani zapis ne smije tvrditi status provjereno. Omjerni KPI s kpi_ratio=true zahtijeva konačan nenulti denominator koji nije bool te definiciju jedinice/brojnika/nazivnika/perioda; nedostatak opisa je warning, nevalidan nazivnik je error. Finansijska tvrdnja na kriteriju zahtijeva benefit_formula, benefit_baseline, benefit_period i benefit_validation_status; to nije samostalna potvrda novčane koristi.

`mevan_report_gate.py:10`: BLOCK ako postoje issues; inače WARN ako postoje warnings; inače PASS. Odobravanje prihvata samo PASS, dakle i WARN blokira finalni snimak. Potrebno je 61 jedinstvenih poznatih kriterija, isti approved/report revision, neprazan reviewer, bez blokiranih/nepotpunih redova. Nema podataka, samoprocjena i neprovjeren dokument upozoravaju; stvarna simulacija upozorava. Za O14/L09/M08 je uvijek eksplicitni risk_reviews reviewed/accepted, i kada je kriterij opravdano N/P. M08 sam po sebi nije dokaz sigurnosnog incidenta. Finansijske tvrdnje traže validation_status=independently_verified i baseline_reference/calculation_reference; sistem provjerava oznaku/reference, ne vrši stvarni nezavisni audit.

Nova pravila v2 ne dodaju generičko upozorenje za opravdan N/P. Historijska v1 imaju raniju ne-praznu provjeru razloga i generički N/P WARN; čitač historijskog snimka koristi njegovu verziju. Ne treba retroaktivno mijenjati stare zaključane nalaze.

## Uzročne hipoteze i odluke

`diagnostic_engine.py:8` ima pet konfigurisanih lanaca: nestabilan plan/kapacitet, kvalitet, zalihe/likvidnost, oprema/zastoji i upravljačka disciplina. U lancu najmanje dva dokumentovana kriterija s ocjenom<=2 daju hipotezu, priority=broj slabih kriterija. Sortira se opadajuće; do tri hipoteze daju odluke s rokom 30 dana. Bez lanaca bira se do tri najniže ocjene <=2, poredak score/code. O14/L09/M08<=2 daju kritični signal za provjeru, nikad tvrdnju da se incident desio. Nema dokazanog kauzalnog modela ili monetizacije iz same ocjene.

## C1/C2/C3 i odabir projekta

`project_candidates.py:8` uzima do 10 odluka iz ai/narrative/decisions/priority_decisions i daje C1…C10. Šifre se filtriraju prema katalogu ulaza ili CODES za v2.0. Naslov najviše 180, why/required_validation 1200. Svi uticaji su neprovjereni/za procjenu, nema izmišljenog ROI.

`project_planner.py:6`: privremene težine profit 25, liquidity 20, delivery 25, risk 20, feasibility 10. Svaki faktor 0–5; **score=round(sum(value×weight/5), 2)**. Potpuno neocijenjen kandidat nije rangiran; potrebno svih pet faktora. Rationale backend 5–1500, UI traži 15 znakova; prazni evidence_ids daju unverified_factors, ne automatsko nezavisno odobrenje. Nepostojeći/dupli kandidat se odbija. Sortiranje: ocijenjeni prvi, score opadajuće, ID leksikografski kod izjednačenja. Poredak nije fiksiran prema naslovu.

Numerički primjer postojećeg regresijskog slučaja: C1 faktori(4, 3, 5, 4, 4) =>20+12+25+16+8=81; C3(3, 5, 3, 4, 3)=>15+20+15+16+6=72; C2(4, 2, 3, 4, 4)=>20+8+15+16+8=67. To su tačni sintetički faktorski vektori iz `browser_approved_smoke.py:52`, u redoslijedu profit/liquidity/delivery/risk/feasibility. Težine nisu promijenjene paketom 2, a njihovo konačno metodološko odobrenje nije poznato.

Planner draft bira ocijenjeni selected_id ili prvi rangirani; početno stanje/ciljevi/checks=false, koristi=[], validacijske aktivnosti i hipoteze. AI pack je dodatni nepotvrđeni prijedlog; ne aktivira projekat. Guided izbor C1/C2/C3 predstavlja prvi/drugi/treći konsultantski prioritet i ne poziva ponovo algoritam ponderisanja; ne poistovjećivati automatski ta dva konteksta oznaka.

## Projekti, plan i statusni prijelazi

`project_execution.py:97` provjerava postoji li već aktivni projekat za isti par company_id/diagnostic_id. Ta provjera je SELECT u aplikaciji, bez djelimičnog unique indeksa. Novi projekat dobija UUIDv4 i status draft. Prelazak draft → validation je dozvoljen; iz draft ili validation može se preći u implementation samo kada su baseline_verified, targets_approved i checks_completed tačni. DEMO implementacija vraća 409. Nema javne rute za zatvaranje ili brisanje projekta, iako se status closed pojavljuje u filterima. Konkurentno kreiranje nije zaštićeno istom SQL jedinstvenošću kao sedmični pregled.

Charter i finansijski scenariji uređuju se samo u draft/validation statusu. Režim real/demo postojećeg projekta ne može se promijeniti. Projektni API ne traži formalnu vezu s approved diagnostic snimkom; tri zastavice su izjave konsultanta, a ne nezavisni dokaz. Izmjena i njen audit upis dijele transakciju.

Sedmični pregled dozvoljen je samo tokom implementacije. Sedmica mora biti stvarna ISO sedmica oblika YYYY-Www. UNIQUE(project_id,week) sprečava drugi pregled iste sedmice. Aktivnosti i KPI unutar lista ostaju dictionary objekti sa slabijom unutrašnjom validacijom od vanjskog modela.

Vođeni tok čuva zasebne bilješke o izvorima i trenutni korak, tri prioriteta te selected_candidate, project_id, owner, start_date i kpi. Projektni nacrt dobija tri aktivnosti s datumima početak +30, +60 i +90 kalendarskih dana. KPI osnovica i cilj su null, a implementacija se ne odobrava automatski.

Za novo odobrenje, summary ima najmanje 80 znakova i 12 riječi. Svaki priority1–3 ima najmanje 40 znakova i šest riječi. Svaki month1–3 ima najmanje 60 znakova i deset riječi. Svako polje ima najviše 6.000 znakova i najmanje četiri različite normalizovane riječi; zamjenske oznake i ponavljanja se odbijaju (`approved_reports.py:21`). To je tehnička provjera potpunosti, ne stručna ocjena kvaliteta. Historijsko preuzimanje traži neprazna polja, ali ne primjenjuje retroaktivno ove strože pragove.

## Finansijski scenariji, stvarni efekti i idempotentnost

`project_finance.py:6` prihvata tačno tri različita scenarija: pesimistični, realni i optimistični. Valuta je KM. Troškovi i iznosi koristi moraju biti nenegativni i najviše 100.000.000.000. Svaki scenarij ima od jedne do 30 koristi, bez duplih naziva nakon trim/casefold normalizacije. Kategorije su operating_saving, contribution_margin, avoided_cost i working_capital_release. Kalkulator prihvata samo estimated; pokušaj potvrde kroz taj kalkulator odbija se.

Bruto godišnji efekat je suma svih kategorija osim jednokratnog obrtnog kapitala. Neto godišnji efekat je bruto efekat umanjen za godišnji trošak rada. ROI je neto godišnji efekat podijeljen troškom implementacije i pomnožen sa 100, samo ako je taj trošak veći od nule. Povrat u mjesecima je trošak implementacije podijeljen pozitivnim neto godišnjim efektom, pomnožen sa 12. U ostalim slučajevima rezultat je None. Novac koristi Decimal i HALF_UP zaokruživanje na dvije decimale. Nema diskontovanja, NPV ili PDV obračuna.

Primjer stvarne formule: operativna korist 12.000 KM, kontribucija 3.000 KM i izbjegnuti trošak 1.000 KM daju bruto 16.000 KM. Uz godišnji trošak 4.000 KM, neto je 12.000 KM. Trošak implementacije od 6.000 KM daje ROI 200% i povrat od šest mjeseci. Oslobađanje obrtnog kapitala od 20.000 KM prikazuje se odvojeno i ne povećava taj ROI. Ako je neto negativan, ROI može biti negativan, ali povrat nije izračunljiv. Nula implementacijskog troška daje None, a ne beskonačan ROI.

`diagnostic_engine.py:68` ima odvojenu aritmetičku kontrolu scenarijskih efekata. Očekivani iznos je apsolutna razlika baseline i target pomnožena s unit_value. Dozvoljeno odstupanje iznosi max(1 KM, 1% deklarisanog iznosa), odnosno veću od te dvije granice. Traže se kategorija hard/avoidance/contribution/working_capital, period, dokaz, odgovarajući status, odsustvo oznake preklapanja i jedinstveni ID. Čak i aritmetički spremna stavka ostaje pending_independent_review u excluded; eligible lista i potvrđene sume ostaju prazni odnosno nula. Ovo nije isto što i projektni ActualIn.

`project_actuals.py:8` zahtijeva period od 4–40 znakova, naziv 3–160, dokaznu referencu 3–1000, obračunsku bilješku 10–2000 i vlasnika izvora 2–160 znakova. Iznos je nenegativan, do 100.000.000.000 KM, s najviše dvije decimale. independent_verification=true nije dozvoljen. Sažetak sabira samo konsultantski potvrđene zapise, odvojeno za ponavljajuće efekte i obrtni kapital, bez pretvaranja u godišnji iznos. Preklapajući periodi ne otkrivaju se automatski.

`project_execution.py:389` koristi kanonski sadržaj: iznos se normalizuje na dvije decimale, tekst trim/NFC postupkom, a JSON sortiranjem ključeva. Bez Idempotency-Key zaglavlja identitet je SHA-256 sadržaja. S ključem je identitet event:key; ključ ima 1–128 ASCII slova, cifara ili znakova . _ : -. UUIDv5 zavisi od projekta i tog identiteta.

BEGIN IMMEDIATE i primarni ključ serijalizuju SQLite upis. Zapis efekta i audit događaj pripadaju istoj transakciji. Ponavljanje istog zahtjeva vraća isti ID, HTTP 201 i replayed=true, bez novog audit događaja. Isti ključ uz izmijenjen iznos vraća 409. Različit ključ dozvoljava zaseban zakoniti događaj istog iznosa. Bez ključa, promijenjeni sadržaj također postaje drugi identitet.

Klijentski JSON id ne određuje identitet jer ga model ne čita. Dva zahtjeva s iznosima 4000 i 4000.00 za isti događaj ostavljaju jedan efekat od 4.000 KM. Stari nasumični UUID zapisi i stari duplikati nisu obrisani ili automatski spojeni. Ova provjerena konkurentna garancija odnosi se na SQLite; PostgreSQL nije skladište actual-effects zapisa.

## DEMO i zaključani izvještaji

`mevan_report_model.py:7` prepoznaje rezervni company_id metalpro-demo, is_simulated i tekst simulacij/simuliran u ulazima. Stvarni snimak odbija takve ulaze. Režim demo zahtijeva svaki primjenjivi red simulation status/is_simulated=true/neprazan dokaz i nema finance_claims; N/P ostaje opravdan i potvrđen. Snimak v2 uključuje cijeli workspace, company/diagnostic indeks, diagnostic_id, gate status, režim i zamrznuti rezultat u SHA256 kanonskog JSON-a (allow_nan=false). Manifest i četiri formata čitaju isti snimak, ne URL režim. PDF oznaka je na svakoj stranici; DOCX header/footer. Hash je integritet baze, nije digitalni potpis vanjskog revizora.

Historijski v1 ostaje čitljiv s policy_version 1 i starim obračunskim putem. Novi v2 ne računa ponovo nakon kasnijih izmjena workspacea. Preimenovanje demo projekta blokirano; postojeći projekat drugog režima se ne povezuje iz Guided toka. Simulacija nije stvarni nalaz, čak ni nakon zaključavanja.

## AI, fallback i granice automatizacije

Backend ima deterministički `/api/v2/analyze` bez AI i četiri generativna endpointa `/api/ai/draft`, `/api/v2/ai-integrated`, `/api/v2/decisions`, `/api/v3/analyze`; projektni `/api/v4/project-ai-pack` je peti AI put. Svi ključ čitaju samo na serveru; bez ključa 503, ne lažni AI rezultat. UI zadržava analizu po pravilima ili preliminarni nacrt, ali ne automatski generativni uspjeh. Chat-completions model default gpt-4.1-mini, ograničeni ulazi i timeoutovi, detalji u [API specifikaciji](FUNCTIONAL_SPECIFICATION.md).

V3 parsira JSON sa sažetkom, do 5 findings, do 3 decisions, do 6 KPI, planom i pitanjima. Backend određuje facts; AI ne smije preračunati indekse/finansije. Kod reindeksira KPI K1…; svaka odluka mora imati validnu nepraznu vezu i gate, nalazi status HIPOTEZA. Kada postoji K6, forsira CCC=DSO+DIO−DPO i opis metode, bez stvarne osnovice. Plan normalizuje do 10 zadataka po periodu, stare string taskove prihvata kao activity i dopunjava prazne opise „Potrebno definisati”. AI ne daje konačno odobrenje. Nisu svi semantički uslovi prompta ujedno strogi validator. AIPlan ima extra=forbid, KPI baseline/target samo None, a assemble vraća sve approval flagove false i prazne finansijske efekte.

## Katalog svih 61 kriterija

Tekstovi ispod prepisani su iz stvarnog `index.html:5`; to su opis/pitanje/preporučeni dokaz/KPI, ne tvrdnja da je dokument priložen ili provjeren. ERP, kupac, proizvod, OEE ili WAPE u tekstu ne znače implementiranu integraciju/kalkulator tog KPI. Skala/validator zajednički su gore i u `data_quality_gate.py:16`/`diagnostic_engine.py:21`; posebnih kriterijskih numeričkih težina/366 ankera nema.

### F01 — Profitabilnost

- Modul: Finansije; ID `F01`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li su EBITDA i marža pouzdano obračunati i analizirani po periodima?
- Preporučeni izvor dokaza: P&L 12–24 mj; usklađenje EBITDA
- KPI/tekst formule ako postoji: EBITDA %; trend
- Finansijski kontekst: Analiza marži i profitnih pokretača
- Preporuka: Analiza marži i profitnih pokretača
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F02 — Kontribucijska marža

- Modul: Finansije; ID `F02`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li je poznata kontribucija po proizvodu, kupcu i narudžbi?
- Preporučeni izvor dokaza: Prodaja; varijabilni troškovi; kalkulacije
- KPI/tekst formule ako postoji: Kontribucija KM/%
- Finansijski kontekst: Profitabilnost portfolija
- Preporuka: Profitabilnost portfolija
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F03 — Struktura troškova

- Modul: Finansije; ID `F03`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se odstupanja materijala, rada, energije i režije objašnjavaju?
- Preporučeni izvor dokaza: Glavna knjiga; centri troška; trend
- KPI/tekst formule ako postoji: Trošak po jedinici
- Finansijski kontekst: Cost-driver analiza
- Preporuka: Cost-driver analiza
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F04 — Standardni troškovi

- Modul: Finansije; ID `F04`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li BOM, normativi i standardi ažurni i upoređeni sa stvarnim?
- Preporučeni izvor dokaza: BOM; radni normativi; variance izvještaji
- KPI/tekst formule ako postoji: Odstupanje standard/stvarno
- Finansijski kontekst: Standard costing
- Preporuka: Standard costing
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F05 — Produktivnost rada

- Modul: Finansije; ID `F05`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se produktivnost povezuje s troškom i iskorištenjem rada?
- Preporučeni izvor dokaza: Sati rada; učinak; obračun plata
- KPI/tekst formule ako postoji: KM/jedinica; jedinica/sat
- Finansijski kontekst: Analiza radnog kapaciteta
- Preporuka: Analiza radnog kapaciteta
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F06 — Škart i dorada

- Modul: Finansije; ID `F06`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se trošak škarta i dorade mjeri po uzroku?
- Preporučeni izvor dokaza: NCR; škart; dorade; vrijednosti materijala
- KPI/tekst formule ako postoji: COPQ KM; škart %
- Finansijski kontekst: Root cause / kvaliteta
- Preporuka: Root cause / kvaliteta
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F07 — Zalihe

- Modul: Finansije; ID `F07`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li su zalihe kontrolisane po obrtnosti, starosti i riziku?
- Preporučeni izvor dokaza: Stanje i starosna struktura zaliha
- KPI/tekst formule ako postoji: DIO; zastarjele zalihe
- Finansijski kontekst: ABC/XYZ i politika zaliha
- Preporuka: ABC/XYZ i politika zaliha
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F08 — Obrtni kapital

- Modul: Finansije; ID `F08`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se potraživanja, obaveze i gotovina aktivno planiraju?
- Preporučeni izvor dokaza: AR/AP aging; cash flow
- KPI/tekst formule ako postoji: DSO; DPO; CCC
- Finansijski kontekst: Working capital program
- Preporuka: Working capital program
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F09 — Budžet i odstupanja

- Modul: Finansije; ID `F09`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se budžet i forecast redovno porede s realizacijom?
- Preporučeni izvor dokaza: Budžet; forecast; mjesečna odstupanja
- KPI/tekst formule ako postoji: Forecast error %
- Finansijski kontekst: Rolling forecast
- Preporuka: Rolling forecast
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F10 — Finansijsko izvještavanje

- Modul: Finansije; ID `F10`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li podaci tačni, pravovremeni i usklađeni s operativom?
- Preporučeni izvor dokaza: Close kalendar; ERP; reconciliations
- KPI/tekst formule ako postoji: Dani do izvještaja
- Finansijski kontekst: Management reporting
- Preporuka: Management reporting
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F11 — Investicije

- Modul: Finansije; ID `F11`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li CAPEX ima business case i post-investicionu provjeru?
- Preporučeni izvor dokaza: CAPEX zahtjevi; ROI/NPV; realizacija
- KPI/tekst formule ako postoji: ROI; payback
- Finansijski kontekst: CAPEX governance
- Preporuka: CAPEX governance
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### F12 — Finansijsko odlučivanje

- Modul: Finansije; ID `F12`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se operativne odluke donose uz finansijske scenarije?
- Preporučeni izvor dokaza: Zapisnici; odluke; KPI izvještaji
- KPI/tekst formule ako postoji: % odluka s analizom
- Finansijski kontekst: Performance governance
- Preporuka: Performance governance
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O01 — Produktivnost rada

- Modul: Operacije; ID `O01`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Komadi ili standardni sati po efektivnom satu rada
- Preporučeni izvor dokaza: Radni nalozi; evidencija sati; normativi
- KPI/tekst formule ako postoji: Učinak / efektivni sati
- Finansijski kontekst: Trošak rada; dodatna kontribucija
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O02 — Iskorištenost kapaciteta

- Modul: Operacije; ID `O02`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Usklađenost opterećenja i raspoloživih kapaciteta
- Preporučeni izvor dokaza: Plan kapaciteta; smjene; stvarna proizvodnja
- KPI/tekst formule ako postoji: Opterećenje / raspoloživi kapacitet
- Finansijski kontekst: Izgubljena marža ili nepotreban trošak
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O03 — OEE / efikasnost opreme

- Modul: Operacije; ID `O03`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Dostupnost, performanse i kvalitet kritične opreme
- Preporučeni izvor dokaza: Dnevnik mašina; zastoji; kvalitet
- KPI/tekst formule ako postoji: OEE = A × P × Q
- Finansijski kontekst: Zastoji; izgubljeni kapacitet
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O04 — Neplanirani zastoji

- Modul: Operacije; ID `O04`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Trajanje, učestalost i uzroci prekida
- Preporučeni izvor dokaza: Dnevnik zastoja; CMMS; smjenski izvještaji
- KPI/tekst formule ako postoji: Min zastoja / planirani sati
- Finansijski kontekst: Trošak zastoja; izgubljena marža
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O05 — Škart i dorada

- Modul: Operacije; ID `O05`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Gubici kvaliteta po proizvodu i uzroku
- Preporučeni izvor dokaza: Kontrola kvaliteta; reklamacije; radni nalozi
- KPI/tekst formule ako postoji: Škart %; FPY; sati dorade
- Finansijski kontekst: Materijal, rad i reklamacije
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O06 — Protočno vrijeme

- Modul: Operacije; ID `O06`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Vrijeme od naloga do završetka proizvodnje
- Preporučeni izvor dokaza: ERP vremenske oznake; VSM; nalozi
- KPI/tekst formule ako postoji: Lead time; WIP
- Finansijski kontekst: Vezana gotovina; kašnjenja
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O07 — Promjene alata / serija

- Modul: Operacije; ID `O07`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Trajanje i standardizacija setupa
- Preporučeni izvor dokaza: Setup evidencije; video analiza; plan
- KPI/tekst formule ako postoji: Prosječan setup (min)
- Finansijski kontekst: Izgubljen kapacitet; veličina serije
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O08 — Standardizovani rad

- Modul: Operacije; ID `O08`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postojanje i primjena standardnih postupaka
- Preporučeni izvor dokaza: Radne instrukcije; audit; Gemba
- KPI/tekst formule ako postoji: Usklađenost sa standardom %
- Finansijski kontekst: Varijacije; kvalitet; produktivnost
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O09 — Tok materijala i WIP

- Modul: Operacije; ID `O09`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Transport, čekanje i međufazne zalihe
- Preporučeni izvor dokaza: Spaghetti mapa; VSM; WIP izvještaji
- KPI/tekst formule ako postoji: WIP dani; udaljenost toka
- Finansijski kontekst: Vezana gotovina; manipulacija
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O10 — Preventivno održavanje

- Modul: Operacije; ID `O10`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Planiranje i izvršenje održavanja
- Preporučeni izvor dokaza: CMMS; planovi; evidencija kvarova
- KPI/tekst formule ako postoji: PM compliance %; MTBF; MTTR
- Finansijski kontekst: Kvarovi; rezervni dijelovi
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O11 — Isporuka iz proizvodnje

- Modul: Operacije; ID `O11`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Poštovanje proizvodnih rokova i količina
- Preporučeni izvor dokaza: Plan i realizacija; ERP; otpremnice
- KPI/tekst formule ako postoji: Plan attainment %; OTD %
- Finansijski kontekst: Penali; hitne smjene; izgubljena prodaja
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O12 — Balansiranje linije

- Modul: Operacije; ID `O12`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Raspodjela rada i ograničenja toka
- Preporučeni izvor dokaza: Mjerenje ciklusa; takt; layout
- KPI/tekst formule ako postoji: Line balance %; takt vs cycle
- Finansijski kontekst: Neiskorišten rad; čekanja
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O13 — Energetska efikasnost

- Modul: Operacije; ID `O13`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Potrošnja energije po jedinici učinka
- Preporučeni izvor dokaza: Računi; mjerenja; evidencija proizvodnje
- KPI/tekst formule ako postoji: kWh / jedinici
- Finansijski kontekst: Energija; emisije
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O14 — Sigurnost i ergonomija

- Modul: Operacije; ID `O14`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Kontrola operativnih rizika i ergonomskih opterećenja
- Preporučeni izvor dokaza: Procjene rizika; incidenti; Gemba
- KPI/tekst formule ako postoji: Incidenti; zatvorene mjere %
- Finansijski kontekst: Povrede; zastoji; rizik
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### O15 — Kontinuirano poboljšavanje

- Modul: Operacije; ID `O15`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Sistem prijedloga, kaizen i održivost mjera
- Preporučeni izvor dokaza: Kaizen registar; audit; KPI trend
- KPI/tekst formule ako postoji: Realizovane mjere / mjesec
- Finansijski kontekst: Zbir verifikovanih koristi
- Preporuka: Poboljšanje prema potvrđenom uzroku
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P01 — Prognoza potražnje

- Modul: Planiranje; ID `P01`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se prognoza zasniva na podacima i redovno mjeri njena tačnost?
- Preporučeni izvor dokaza: Prognoza, narudžbe, istorija prodaje
- KPI/tekst formule ako postoji: WAPE, bias
- Finansijski kontekst: Neadekvatna proizvodnja; višak/manjak zaliha
- Preporuka: Segmentirati prognoze; pratiti WAPE i bias
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P02 — S&OP / IBP

- Modul: Planiranje; ID `P02`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoji li redovan proces usaglašavanja prodaje, operacija i finansija?
- Preporučeni izvor dokaza: Zapisnici S&OP, scenariji, odobren plan
- KPI/tekst formule ako postoji: Usklađenost plana; broj eskalacija
- Finansijski kontekst: Nerealni planovi, izgubljena marža
- Preporuka: Uvesti mjesečni S&OP i sedmično izvršno usklađivanje
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P03 — Glavni plan proizvodnje

- Modul: Planiranje; ID `P03`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoji li realan, zamrznut i rolling plan proizvodnje?
- Preporučeni izvor dokaza: MPS, sedmični plan, promjene verzija
- KPI/tekst formule ako postoji: Plan attainment; schedule adherence
- Finansijski kontekst: Prekovremeni rad, hitne izmjene
- Preporuka: Rolling plan 6+ sedmica; pravila zamrzavanja
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P04 — Planiranje kapaciteta

- Modul: Planiranje; ID `P04`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se plan provjerava prema ljudima, mašinama i uskim grlima?
- Preporučeni izvor dokaza: RCCP, kapaciteti, smjene, takti
- KPI/tekst formule ako postoji: Opterećenje kritičnog resursa
- Finansijski kontekst: Čekanja, gubitak prodaje
- Preporuka: RCCP i TOC analiza ograničenja
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P05 — MRP i materijalne potrebe

- Modul: Planiranje; ID `P05`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li materijalni zahtjevi vezani za tačan BOM i plan?
- Preporučeni izvor dokaza: BOM, MRP izuzeci, rezervacije
- KPI/tekst formule ako postoji: Stockout; planirani vs stvarni utrošak
- Finansijski kontekst: Prekidi rada, višak nabavke
- Preporuka: Urediti BOM i MRP parametre
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P06 — Pouzdanost dobavljača

- Modul: Planiranje; ID `P06`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se prate rok, kvalitet i rizik dobavljača?
- Preporučeni izvor dokaza: Narudžbenice, prijemi, reklamacije
- KPI/tekst formule ako postoji: Supplier OTD; PPM
- Finansijski kontekst: Hitni transport, zastoji
- Preporuka: Segmentacija dobavljača i scorecard
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P07 — Politika zaliha

- Modul: Planiranje; ID `P07`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li sigurnosne zalihe, ABC/XYZ i obrt definisani?
- Preporučeni izvor dokaza: Stanje zaliha, starost, inventure
- KPI/tekst formule ako postoji: DIO; obrt; obsolete %
- Finansijski kontekst: Vezana gotovina, otpis
- Preporuka: ABC/XYZ i parametri dopune
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P08 — Tačnost ERP podataka

- Modul: Planiranje; ID `P08`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li stanja, rokovi, BOM i rute pouzdani i ažurni?
- Preporučeni izvor dokaza: ERP transakcije, inventure, master data
- KPI/tekst formule ako postoji: Inventory accuracy; BOM accuracy
- Finansijski kontekst: Pogrešne odluke, zastoji
- Preporuka: Master-data governance i dnevno knjiženje
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P09 — Realizacija proizvodnog plana

- Modul: Planiranje; ID `P09`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se dnevno mjeri izvršenje i analiziraju odstupanja?
- Preporučeni izvor dokaza: Dnevni plan/realizacija, razlozi
- KPI/tekst formule ako postoji: Plan attainment %
- Finansijski kontekst: Kašnjenja, neplanirani rad
- Preporuka: Dnevni tier sastanci i Pareto odstupanja
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P10 — Pouzdanost isporuka

- Modul: Planiranje; ID `P10`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li su rokovi kupcima realni i mjerljivo ispunjeni?
- Preporučeni izvor dokaza: Narudžbe, otpremnice, reklamacije
- KPI/tekst formule ako postoji: OTIF; OTD
- Finansijski kontekst: Penali, izgubljeni kupci
- Preporuka: ATP/CTP i kontrola obećanih rokova
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P11 — Interna i izlazna logistika

- Modul: Planiranje; ID `P11`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li su tokovi materijala i otpreme stabilni?
- Preporučeni izvor dokaza: Tok materijala, skladišne lokacije
- KPI/tekst formule ako postoji: Vrijeme manipulacije; trošak transporta
- Finansijski kontekst: Čekanje, dodatna manipulacija
- Preporuka: VSM, milk-run, standard skladišta
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### P12 — Upravljanje odstupanjima

- Modul: Planiranje; ID `P12`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoje li vlasnici, rokovi i zatvaranje uzroka odstupanja?
- Preporučeni izvor dokaza: Action log, eskalacije, zapisnici
- KPI/tekst formule ako postoji: On-time action closure %
- Finansijski kontekst: Ponavljanje problema
- Preporuka: PDCA, vlasnik akcije i sedmični review
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L01 — Organizaciona struktura

- Modul: Ljudi; ID `L01`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li funkcije, linije izvještavanja i zamjene jasno definisane?
- Preporučeni izvor dokaza: Organigram, opisi poslova, intervjui
- KPI/tekst formule ako postoji: Udio ključnih uloga s dokumentovanom odgovornošću
- Finansijski kontekst: Nejasne odluke, čekanja
- Preporuka: Definisati RACI i organizacionu mapu
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L02 — Odgovornost za rezultate

- Modul: Ljudi; ID `L02`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Ima li svaki KPI imenovanog vlasnika i ritam praćenja?
- Preporučeni izvor dokaza: KPI izvještaji, zapisnici, RACI
- KPI/tekst formule ako postoji: Udio KPI s vlasnikom i akcijom
- Finansijski kontekst: Nepreuzeta odstupanja
- Preporuka: KPI ownership i sedmični review
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L03 — Kompetencije rukovodilaca

- Modul: Ljudi; ID `L03`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Mogu li rukovodioci planirati, voditi i rješavati probleme?
- Preporučeni izvor dokaza: Intervjui, simulacije, evaluacije
- KPI/tekst formule ako postoji: Udio procijenjenih rukovodilaca
- Finansijski kontekst: Loše odluke i eskalacije
- Preporuka: Individualni razvojni planovi
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L04 — Matrica vještina

- Modul: Ljudi; ID `L04`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li ključne operativne vještine evidentirane i pokrivene?
- Preporučeni izvor dokaza: Matrice vještina, certifikati, provjera na radnom mjestu
- KPI/tekst formule ako postoji: Pokrivenost kritičnih operacija (%)
- Finansijski kontekst: Zastoji zbog odsustva
- Preporuka: Uvesti skill matrix i cross-training
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L05 — Uvođenje i obuka

- Modul: Ljudi; ID `L05`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoji li standardan onboarding i provjera osposobljenosti?
- Preporučeni izvor dokaza: Planovi obuke, testovi, evidencije
- KPI/tekst formule ako postoji: Vrijeme do samostalnosti (dani)
- Finansijski kontekst: Škart i duži onboarding
- Preporuka: Standardizovati onboarding
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L06 — Upravljanje učinkom

- Modul: Ljudi; ID `L06`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoje li jasni ciljevi, feedback i korektivne aktivnosti?
- Preporučeni izvor dokaza: Ciljevi, evaluacije, sastanci
- KPI/tekst formule ako postoji: Udio realizovanih razvojnih mjera
- Finansijski kontekst: Slaba produktivnost
- Preporuka: Mjesečni performance review
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L07 — Komunikacija i eskalacija

- Modul: Ljudi; ID `L07`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li problemi brzo dolaze do osobe koja ih može riješiti?
- Preporučeni izvor dokaza: Zapisnici smjena, eskalacijske procedure
- KPI/tekst formule ako postoji: Prosječno vrijeme eskalacije (h)
- Finansijski kontekst: Čekanja i kašnjenja
- Preporuka: Daily management i eskalacijska matrica
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L08 — Angažovanost i zadržavanje

- Modul: Ljudi; ID `L08`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Znamo li uzroke odlazaka i prepreke angažmanu?
- Preporučeni izvor dokaza: Fluktuacija, exit intervjui, ankete
- KPI/tekst formule ako postoji: Dobrovoljna fluktuacija (%)
- Finansijski kontekst: Trošak zamjene i obuke
- Preporuka: Analiza uzroka i plan zadržavanja
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L09 — Sigurnost i kultura odgovornosti

- Modul: Ljudi; ID `L09`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Prijavljuju li se rizici i provode preventivne mjere?
- Preporučeni izvor dokaza: Evidencije incidenata, obuke, obilazak
- KPI/tekst formule ako postoji: Zatvorene preventivne mjere (%)
- Finansijski kontekst: Povrede i prekidi rada
- Preporuka: Preventivni safety review
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### L10 — Nasljeđivanje i održivost

- Modul: Ljudi; ID `L10`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Može li sistem funkcionisati bez ključnog pojedinca ili konsultanta?
- Preporučeni izvor dokaza: Plan nasljeđivanja, zamjene, audit
- KPI/tekst formule ako postoji: Udio kritičnih funkcija s obučenom zamjenom
- Finansijski kontekst: Zavisnost od pojedinca
- Preporuka: Mentorstvo i plan sukcesije
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M01 — Strategija i ciljevi

- Modul: Upravljanje; ID `M01`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li su godišnji i kvartalni ciljevi mjerljivi i povezani s proizvodnjom?
- Preporučeni izvor dokaza: Strateški plan, godišnji ciljevi, KPI stablo
- KPI/tekst formule ako postoji: Udio ciljeva sa vlasnikom i mjerom
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Hoshin Kanri / KPI cascade
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M02 — Uloge i prava odlučivanja

- Modul: Upravljanje; ID `M02`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li vlasnici procesa, ovlaštenja i eskalacije jasno određeni?
- Preporučeni izvor dokaza: RACI, sistematizacija, matrica ovlaštenja
- KPI/tekst formule ako postoji: Udio procesa s jasnim vlasnikom
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: RACI i governance
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M03 — Dnevno upravljanje

- Modul: Upravljanje; ID `M03`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoje li dnevni sastanci s odstupanjima, akcijama i odgovornima?
- Preporučeni izvor dokaza: Dnevne table, zapisnici, dnevni izvještaji
- KPI/tekst formule ako postoji: Udio zatvorenih dnevnih akcija
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Daily Management System
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M04 — KPI arhitektura

- Modul: Upravljanje; ID `M04`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li KPI definisani, tačni i povezani s poslovnim rezultatom?
- Preporučeni izvor dokaza: KPI katalog, definicije, izvori podataka
- KPI/tekst formule ako postoji: Udio KPI s definicijom i izvorom
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: KPI dictionary / tier meetings
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M05 — Ritam poslovnih pregleda

- Modul: Upravljanje; ID `M05`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Održavaju li se sedmični i mjesečni pregledi rezultata?
- Preporučeni izvor dokaza: Agende, zapisnici, odluke
- KPI/tekst formule ako postoji: Pravovremenost i realizacija odluka
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Management review cadence
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M06 — Upravljanje odstupanjima

- Modul: Upravljanje; ID `M06`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Istražuju li se sistemski uzroci ponovljenih odstupanja?
- Preporučeni izvor dokaza: A3, 5 Why, CAPA evidencije
- KPI/tekst formule ako postoji: Udio ponovljenih problema
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: A3 / DMAIC / CAPA
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M07 — Izvršenje akcionih planova

- Modul: Upravljanje; ID `M07`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoji li jedinstvena evidencija mjera, rokova i statusa?
- Preporučeni izvor dokaza: Akcioni planovi, historija zatvaranja
- KPI/tekst formule ako postoji: On-time action closure %
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Action tracking / escalation
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M08 — Upravljanje rizicima

- Modul: Upravljanje; ID `M08`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Prepoznaju li se operativni, finansijski i kontinuitetni rizici?
- Preporučeni izvor dokaza: Registar rizika, FMEA, plan kontinuiteta
- KPI/tekst formule ako postoji: Udio visokih rizika s mjerama
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Risk register / FMEA
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M09 — Upravljanje promjenama

- Modul: Upravljanje; ID `M09`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Da li se promjene testiraju, komuniciraju i stabilizuju?
- Preporučeni izvor dokaza: Pilot zapisi, SOP revizije, obuke
- KPI/tekst formule ako postoji: Udio promjena održanih 90 dana
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: PDCA / change management
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M10 — Digitalni podaci i ERP disciplina

- Modul: Upravljanje; ID `M10`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Jesu li transakcije pravovremene, tačne i sljedive?
- Preporučeni izvor dokaza: ERP logovi, usklađenja, audit trail
- KPI/tekst formule ako postoji: Tačnost i pravovremenost knjiženja
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Data governance / ERP controls
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M11 — Međufunkcionalna koordinacija

- Modul: Upravljanje; ID `M11`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Usklađuju li se prodaja, proizvodnja, nabavka i finansije?
- Preporučeni izvor dokaza: S&OP zapisnici, konfliktni prioriteti
- KPI/tekst formule ako postoji: Udio riješenih međufunkcionalnih blokada
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: S&OP / cross-functional governance
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.

### M12 — Kontinuirano poboljšanje i održivost

- Modul: Upravljanje; ID `M12`. Izvor: `index.html:5`.
- Pitanje/šta mjeri: Postoje li redovne inicijative i provjera održivosti efekata?
- Preporučeni izvor dokaza: Kaizen registar, audit 30/60/90
- KPI/tekst formule ako postoji: Udio potvrđenih održivih poboljšanja
- Finansijski kontekst: Upravljanje učinkom
- Preporuka: Kaizen / sustain audit
- Težina: jednaka ostalim uključenim kriterijima; 20/N po jedinici ocjene, bez posebnog pondera. Validator: cijeli 0–5 ili dokumentovan N/P, statusni/metapodatkovni gate; nema posebnog automatskog kalkulatora ovog kriterija.
