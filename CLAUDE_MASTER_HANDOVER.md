> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: samostalne upute za siguran prenos i nastavak postojećeg proizvoda.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# CLAUDE – MASTER PROJECT HANDOVER

## Svrha i obavezni način nastavka

Nastavi postojeći MEVAN proizvod, nemoj praviti novu aplikaciju ili generički SaaS. Ovo je privatna konsultantska dijagnostika proizvodnih kompanija: 61 kriterij, 5 modula, ljudski pregled, dokazna ograničenja, projekti i 90 dana. Primarni autoritet za implementaciju je preneseni kod commita `132ef288917b0573709655437cb8904574898015`; razgovor/dokument ne dokazuje funkciju ako je nema u kodu. Dokumentacija je snapshot, ne odobrenje novih promjena.

## Lokalno, GitHub i hosting su tri različita stanja

| Površina | Zabilježena verzija | Dokaz / granica |
|---|---|---|
| Lokalni kod | `132ef288917b0573709655437cb8904574898015` | Ponovo read-only potvrđeni HEAD/status u ovom zadatku; paket 2 |
| GitHub `mevan-v2-test` | `be879956ea6ebdc7fc4106459080d3ae85c6202c` | Prethodno potvrđeno spajanje [PR #1](https://github.com/mevan-platform/mevan-diagnostic/pull/1); lokalni remote-tracking ref, bez novog fetch-a |
| Render `mevan-diagnostic-v2-test` | `85fd230eb7d781bb6d25b3e8f1552f8e54f31a2b`, Live; Auto-Deploy Off | Izvorni chat je prijavljeno read-only provjerio dashboard, granu `mevan-v2-test` i [adresu](https://mevan-diagnostic-v2-test.onrender.com); nije nova cloud provjera |

Claude koji samo klonira GitHub **ne dobija paket 2**. Izvori lokalnog commita prenose se patchom na potvrđenu merge osnovu; patch sam ne kreira originalni commit SHA. Nema automatskog deploya iz same predaje; Render postavke se ne mijenjaju.

## Pravila koja se ne smiju izgubiti

Prva verzija koristi bosanski u korisničkim porukama i novoj dokumentaciji. Engleski ostaje za kasniju fazu; stari engleski naslovi predstavljaju dug u lokalizaciji.

Sačuvaj postojeće podatke, funkcionalnosti, testne rezultate, izvještaje i izvorne grane. Ne briši niti automatski spajaj stare finansijske efekte. Ne prepisuj historijska odobrenja.

N/P zahtijeva smislen razlog i imenovanu potvrdu konsultanta. Izuzima se iz nazivnika, a prazan primjenjivi skup ostaje None i prikazuje se kao „Neocjenjivo”. Nedokazani primjenjivi kriteriji i dalje blokiraju stvarni izvještaj. Kritični rizici O14, L09 i M08 zahtijevaju eksplicitan pregled.

DEMO režim mora biti eksplicitan i vezan uz zaključani snimak i manifest. Oznaka „DEMO — simulirani podaci” ostaje u interfejsu i sva četiri zaključana PDF/DOCX izlaza. Simulacija nije stvarno konsultantsko odobrenje ili verifikacija. DEMO projekat se ne može preimenovati u stvarni niti odobriti za implementaciju. URL parametar nije autoritet za režim.

Ne mijenjaj privremene težine C1/C2/C3: 25/20/25/20/10. Isti sintetički ulaz mora zadržati poredak C1 81, C3 72 i C2 67. Guided izbor jednog od tri unesena prioriteta nije promjena algoritma rangiranja kandidata.

AI priprema nacrt. Deterministički backend ostaje autoritet za izračunate indekse i finansijske činjenice. Oznaka proof=confirmed i tekst dokaza nisu nezavisna provjera. Iz samog AI teksta ne nastaju potvrđeni finansijski efekti.

Očuvaj popravke prvog paketa: ponovljeni zahtjev za 4.000 KM ostaje jedan efekat; isti ključ s drugim sadržajem daje 409; zakoniti različiti događaji ostaju dozvoljeni. Sedam polja popunjenih sa „x” ne prolazi novo odobrenje, dok raniji odobren kratak sadržaj ostaje čitljiv. Word QA mora zadržati sve postojeće provjere.

Push, PR, direktni upis u main ili baznu granu, promjena Render postavki, deploy i produkcijska migracija zahtijevaju zasebnu izričitu korisničku odluku. Ova predaja odobrava samo dokumentaciju i pripremu prenosa izvora.

## Arhitektura koju preuzimaš

Backend je FastAPI/Python, frontend je postojeći statički HTML/JavaScript, a osnovno skladište je SQLite. `server.py` sadrži autentifikaciju i glavne rute. `index.html` upravlja legacy radnim prostorom, dijagnostikom, nacrtima i ručnim Word izvozom. `diagnostic_engine.py` računa indekse i priprema determinističke hipoteze.

`data_quality_gate.py` i `mevan_report_gate.py` provjeravaju zapise i završni gate. Moduli `mevan_test_*` čuvaju revizije, zaključane snimke i manifest te izlažu postojeći TEST API. `approved_reports.py` generiše dva prikaza u dva formata. `diagnostic_review.html` sadrži vođeni tok.

`project_execution.py` izlaže projekte, kandidate, finansije, efekte, audit i dashboard. Moduli project_planner, project_candidates, project_finance, project_actuals, project_ai_pack i project_reports nose njihove poslovne račune i izvoze. PostgreSQL je opcionalan samo za kandidat nacrte; migracija za tu šemu nije pronađena.

Legacy i TEST radni prostor imaju odvojene CAS ugovore i nisu jedna atomska transakcija. Lokalni storage nije serverska baza. Kompanijski i dijagnostički tekstualni identifikatori nisu tenant autorizacija. Postoji jedan administrator, bez registracije, pretplata ili drugih generičkih SaaS funkcija. Potpuni inventari sadrže 45 kombinacija API metode i putanje te 125 definicija testova.

## Siguran prenos izvora lokalnog commita — kumulativni patch

Korisnik sam prenosi ZIP. Paket ne sadrži stvarne baze, API ključeve, prijavne tajne ili klijentske priloge. Kumulativni patch prenosi svih 19 izmijenjenih izvornih, testnih i dokumentacijskih datoteka iz lokalnog paketa 2 u odnosu na merge osnovu. Izvorni commit je `132ef288917b0573709655437cb8904574898015`, a njegova osnova `be879956ea6ebdc7fc4106459080d3ae85c6202c`.

Git bundle je lokalno napravljen i provjeren, ali **nije uključen u ZIP**: tačan Git commit u svojim metapodacima zadržava stvarni identitet autora. Radi korisničkog zahtjeva da predaja ne kopira stvarne identitete, izabrana je dopuštena alternativa — patch i anonimizirani source archive. Ne treba pokušavati promijeniti autora i tvrditi da SHA ostaje isti. Autoritativni SHA porijekla ostaje zabilježen, dok sigurni prenos dokazuje jednakost stabla izvora.

U lokalnom klonu koji sadrži merge osnovu, iz čistog radnog stabla:

```bash
HANDOVER_DIR='/apsolutna/putanja/mevan-handover-20261110'
cd "$HANDOVER_DIR"
sha256sum -c SHA256SUMS
cd '/apsolutna/putanja/lokalnog-klona/mevan-diagnostic'
git status --short --branch
# Ne nastavljati ako postoje korisnikove izmjene; ništa ne resetovati ili brisati.
git cat-file -e be879956ea6ebdc7fc4106459080d3ae85c6202c^{commit}
git switch -c handover/mevan-paket2-patch be879956ea6ebdc7fc4106459080d3ae85c6202c
git apply --check "$HANDOVER_DIR/prenos/mevan-paket2.patch"
git apply --index "$HANDOVER_DIR/prenos/mevan-paket2.patch"
git diff --cached --check
git write-tree
# Očekivano stablo izvora: a6a6e45978fc801dfba8b2adda946b5ccca8d540
```

Ako grana već postoji, odabrati drugo novo ime nakon provjere; ne prepisivati je. Ako lokalni klon nema merge osnovu, nabaviti je iz pouzdanog repozitorija tek uz operatorov ovlašten pristup. Ovaj dokumentacijski zadatak nije radio mrežni fetch. Ne primjenjivati patch na proizvoljnu noviju bazu bez pregleda razlike i konflikata.

Primjena patcha ne kreira originalni commit: HEAD ostaje merge osnova, a izmjene su u indeksu i radnom stablu nove grane. Eventualni novi lokalni commit obično ima drugi SHA zbog metapodataka. Ne tvrditi da `git rev-parse HEAD` poslije samog patcha vraća originalni 132ef28. Za potpun identitet izvornog commita bio bi potreban izvorni Git objekt i njegovi metapodaci, što ovaj anonimizirani ZIP namjerno ne prenosi.

`provjere/prenos.json` potvrđuje da je patch primijenjen u zasebnom privremenom repozitoriju i da `git write-tree` odgovara stablu lokalnog commita. To je provjera prenosa, a ne ponovno pokretanje aplikacijskih testova. Nema automatskog commita, pusha, PR-a ili deploya. Patch ne prenosi baze ili tajne.

## Alternativa — source archive bez Git historije

`prenos/mevan-source-132ef28.tar.gz` je git archive izvora tog commita, ali namjerno bez praćenog `.env.example` (stvarna e-mail adresa). Zaseban siguran `config.env.example` ima prazne tajne i example.invalid identitet. Sve ostale praćene datoteke archive-a provjerene su prema navedenom commitu. Archive omogućava čitanje, pokretanje i testiranje izvora, ali bez `.git` ne daje ancestor/commit identitet za nastavak Git historije. Za nastavak Git rada koristiti patch na potvrđenoj osnovi i provjeriti stablo izvora. Nema venv-a, baza, generisanih izvještaja ili nepraćenih fajlova.

## Setup i prvo čitanje

1. Pročitaj [MASTER_PROJECT](MASTER_PROJECT.md), [poslovnu logiku](BUSINESS_LOGIC.md), [arhitekturu](DATABASE_AND_ARCHITECTURE.md) i [sigurnost](SECURITY.md). Zatim [funkcionalni API](FUNCTIONAL_SPECIFICATION.md), [UX](UI_UX_SPECIFICATION.md), [admin](ADMIN_PANEL.md), [infra](INFRASTRUCTURE_AND_DEPLOYMENT.md), [QA](TESTING_AND_QA.md) i [roadmap](ROADMAP_AND_KNOWN_ISSUES.md).
2. Provjeri HEAD/status, manifest i stablo izvora nakon patcha. Ne miješaj lokalni `132ef28`, GitHub `be87995` i Render `85fd230`. Sam klon GitHuba nema paket 2.
3. Pregledaj AGENTS/upute u novom lokalnom okruženju prije bilo kakvih promjena. U ovoj predaji nije pronađen repo AGENTS; kasnije okruženje može imati svoje upute.
4. Napravi venv, instaliraj requirements i test alate prema infra dokumentu. Postavi vlastite lokalne tajne i novu temp DB; bez stvarnog OPENAI/PG ključa za offline QA. Nema automatskog .env loadera.
5. Ne ponavljaj uspješne testove radi samog dokumentovanja. Nakon konkretne izmjene pokreni relevantne regresije i obavezne provjere; čuvaj nove logove odvojeno. Ne proglašavaj mock AI ili SQLite test udaljenim produkcijskim dokazom.

## Očekivani regresijski reperi

Sačuvani rezultat drugog paketa je 168 prolaza uz jedno upozorenje. Word QA prolazi 12/12, a oba mobilna toka prolaze. Novi browser test za Guided tok nije korak trenutnog CI workflowa. Prvi uspješan CI imao je 136 prolaza, Word 12/12 i Chromium provjeru; odnosi se na head `2a31e358c1d7c72f79c4acb25907dabd9ba34fb5` i run 42899507229.

Za isti primjenjivi rangirani uzorak očekuj C1 81, C3 72 i C2 67. Dva identična zahtjeva za 4.000 KM moraju ostaviti jedan efekat; zasebna legitimna oznaka događaja može dati drugi zapis. Kada su svi kriteriji N/P, indeks mora biti None i prikazan kao „Neocjenjivo”. Sva četiri DEMO formata zadržavaju oznaku, a promjena URL parametra ne mijenja režim. Historijski snimak v1 ostaje čitljiv; kasnije promjene radnih ocjena ne mijenjaju zamrznuti obračun v2.

Vizuelni render DOCX dokumenata nije potvrđen. Reprezentativni PDF uzorci jesu pregledani. Nemoj te dvije vrste dokaza spajati u jednu tvrdnju.

## Podaci i kompatibilnost

Ne diraj postojeće baze. UI JSON backup pokriva samo legacy workspace, a TEST snapshot samo TEST workspace. Puni SQLite backup uključuje audit, projekte i odobrenja iste datoteke baze, ali ne zaseban PostgreSQL ili vanjske priloge. CLI restore dozvoljava samo novu putanju.

Snimci v1 zadržavaju ranija pravila i čitač. Snimci v2 čuvaju režim i zamrznuti model obračuna. Nemoj pretvarati stare nalaze u nove bez nove stručne revizije. Konačni bajtovi PDF/DOCX izvještaja nisu automatski arhivirani. Slabije list/dict šeme i različiti nazivi ključeva rokova zahtijevaju kompatibilno proširenje, a ne masovno preimenovanje bez migracijskog plana.

## Šta ostaje nepoznato

Puna originalna historija/prilozi, D-001–D-100, 366 ankera i konačno metodološko odobrenje težina nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor, cloud nije. Stvarni AI, udaljeni PG, Render live provjera, Word vizuelna paginacija i nezavisna sigurnosna validacija nisu potvrđeni. Ove granice zadrži u budućim izvještajima. Prijedlog asistenta ne pretvaraj u korisničku odluku.

Sljedeći funkcionalni korak mora biti konkretno odobren novi paket. Ne započinji novu implementaciju samo zato što postoji roadmap ili ova predaja.
