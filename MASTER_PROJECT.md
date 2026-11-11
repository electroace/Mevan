> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: pregled proizvoda, odluka, statusa, pokrivenosti i prenosnog paketa.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — glavni projektni dokument

MEVAN je postojeći privatni demonstracijski alat za konsultantsku dijagnostiku proizvodnih kompanija i vođenje validacijskih/operativnih projekata. Procjenjuje pet oblasti kroz 61 kriterij, razdvaja procjenu od dokaza, priprema determinističku i opcionalnu AI podršku te omogućava ljudski pregled, zaključane izvještaje i praćenje projekta. Niska zrelost sama ne dokazuje finansijski gubitak ili uzrok.

Backend je FastAPI/Python s jednom env administratorskom prijavom; frontend je postojeći HTML/CSS/JavaScript bez build frameworka. Glavni SQLite JSON workspace, revizionisani TEST workspace i projektne tabele paralelno postoje. PostgreSQL je samo opcija za nacrte ocjena kandidata. Ne praviti novu aplikaciju za nastavak razvoja.

## Lokalno, GitHub i hosting su tri različita stanja

| Površina | Zabilježena verzija | Dokaz / granica |
|---|---|---|
| Lokalni kod | `132ef288917b0573709655437cb8904574898015` | Ponovo read-only potvrđeni HEAD/status u ovom zadatku; paket 2 |
| GitHub `mevan-v2-test` | `be879956ea6ebdc7fc4106459080d3ae85c6202c` | Prethodno potvrđeno spajanje [PR #1](https://github.com/mevan-platform/mevan-diagnostic/pull/1); lokalni remote-tracking ref, bez novog fetch-a |
| Render `mevan-diagnostic-v2-test` | `85fd230eb7d781bb6d25b3e8f1552f8e54f31a2b`, Live; Auto-Deploy Off | Izvorni chat je prijavljeno read-only provjerio dashboard, granu `mevan-v2-test` i [adresu](https://mevan-diagnostic-v2-test.onrender.com); nije nova cloud provjera |

Claude koji samo klonira GitHub **ne dobija paket 2**. Izvori lokalnog commita prenose se priloženim patchom; on čuva stablo izvora, ali sam ne kreira originalni commit SHA. Nema automatskog deploya iz same predaje; Render postavke se ne mijenjaju.

## Historija, izričite odluke i precedence

Dostupni izvori: korisničke poruke u ovoj niti; `docs/MEVAN_REGISTAR_AKTIVNOSTI_v8.md`; `MEVAN_4_0_KORAK_3_STATUS.md` do postojećeg koraka 23 (nisu sve numeričke datoteke prisutne); `docs/PRVI_PAKET_20261110.md`; `docs/DRUGI_PAKET_20261110.md`; postojeći izvještaji analize izvan repozitorija. Status dokumenta „završeno” nije dokaz da je korisnik odobrio svaku njegovu preporuku.

1. Početno je odobrena samo analiza i plan; izričito je tražen nastavak postojeće aplikacije, 61 kriterij/5 modula, AI, trajni C1/C2/C3, PDF/DOCX, sažetak i 90 dana, vođeno prikupljanje, jednostavniji premium mobilni tok i stabilan PIT demo 3–4.12.2026. Prva verzija samo bosanski; engleski kasnije.
2. Raniji N/P detalji i DEMO režim bili su prijedlozi, bez odobrenja. Kasnije izričito odobren prvi paket obuhvatio je samo idempotentne efekte, tehničku validaciju pregleda i stvarni uzrok pada Word QA. Zatim su zasebno odobreni commit/push/PR, read-only review, CI izmjena i spajanje PR #1, bez deploya.
3. Prvi paket i CI spojeni su u `mevan-v2-test` na `be879956ea6ebdc7fc4106459080d3ae85c6202c`. PR #1 je prema prethodno potvrđenom stanju merged. CI odobrenog heada `2a31e358c1d7c72f79c4acb25907dabd9ba34fb5` završio je uspješno: [Actions 42899507229](https://github.com/mevan-platform/mevan-diagnostic/actions/runs/42899507229). Ovo nisu novi mrežni upiti.
4. Najnovije implementacijsko odobrenje je paket 2 na novoj lokalnoj grani: opravdan N/P s konsultantskom potvrdom i izuzimanjem, eksplicitni trajni DEMO te vođeni tok. Time su R-18/R-19 dobili izričito odobrenje samo u tom opsegu. Nisu promijenjene težine C1/C2/C3. Lokalni commit je `132ef288917b0573709655437cb8904574898015`, bez pusha/PR-a/deploya.
5. Sadašnji zadatak je samo dokumentacija i prenos lokalnog koda. Ne daje novo odobrenje za implementaciju, push, spajanje ili hosting.

Prioritet: posljednja konkretna izričita korisnička odluka za dati opseg > ranija odluka za isti opseg > prijedlog asistenta. Nepotvrđene preporuke (benchmark, stručna kalibracija, konačni dizajn ili budući tenant model) ne postaju odobrene samim postojanjem dokumenta. Nedostupni D-001–D-100 ne mogu se rekonstruisati iz grupnih opisa. CSV 366 ankera nije verifikovan; postoje samo vidljive opće skale i pitanja.

## Sadržaj i redoslijed čitanja


| Dokument | Svrha |
| --- | --- |
| [MASTER_PROJECT.md](MASTER_PROJECT.md) | Ovaj pregled i pravila predaje |
| [BUSINESS_LOGIC.md](BUSINESS_LOGIC.md) | Sve formule, katalog 61 kriterija, gate i primjeri |
| [FUNCTIONAL_SPECIFICATION.md](FUNCTIONAL_SPECIFICATION.md) | Svi API ugovori i funkcionalni tokovi |
| [DATABASE_AND_ARCHITECTURE.md](DATABASE_AND_ARCHITECTURE.md) | Sve tabele/kolone/indeksi i JSON arhitektura |
| [UI_UX_SPECIFICATION.md](UI_UX_SPECIFICATION.md) | Sve stranice, kontrole, interakcije i paralelni tokovi |
| [ADMIN_PANEL.md](ADMIN_PANEL.md) | Stvarne administratorske mogućnosti i odsutne funkcije |
| [SECURITY.md](SECURITY.md) | Kodirane kontrole, rizici i granice dokaza |
| [INFRASTRUCTURE_AND_DEPLOYMENT.md](INFRASTRUCTURE_AND_DEPLOYMENT.md) | Zavisnosti, lokalni setup, CI i hosting granice |
| [TESTING_AND_QA.md](TESTING_AND_QA.md) | Potpuni inventar testova i poznati rezultati |
| [ROADMAP_AND_KNOWN_ISSUES.md](ROADMAP_AND_KNOWN_ISSUES.md) | Statusi, dug, ograničenja i otvorene odluke |
| [CLAUDE_MASTER_HANDOVER.md](CLAUDE_MASTER_HANDOVER.md) | Samostalne početne upute za Claude |


## Trenutna tehnička spremnost

Implementirano i lokalno regresijski provjereno: prvi paket, N/P v2, četiri označena DEMO izvoza, trajni vođeni tok, projekti/kandidati/scenariji/efekti. Djelimično: lokalizacija cijelog starog interfejsa, produkcijska sigurnost, stručna validacija sadržaja i kvalitet dokaza. Neimplementirano: korisničke uloge/registracija/billing/tenant autorizacija/upload priloga. Neprovjereno: stvarni AI odgovor, udaljeni PostgreSQL, živa Render verzija iz ovog okruženja, vizuelna DOCX paginacija. Detalji su u [roadmapu](ROADMAP_AND_KNOWN_ISSUES.md).

## Pokrivenost i provjera ove dokumentacije

Inventar je izrađen iz AST-a svih praćenih Python datoteka, registriranih OpenAPI putanja i statičkog skeniranja svih praćenih HTML/JS datoteka te login HTML-a u serveru. Rezultat: **45 parova metoda/putanja na 37 putanja**, **10 aplikacijskih tabela + interna sqlite_sequence**, **61 kriterij**, **125 definicija testnih metoda/funkcija**, **168 parametrizovanih prethodnih testnih slučajeva**, **217 definicija HTML/JS kontrola**, **195 unosa imenovanih JS funkcija/vezivanja događaja**. Ovo nisu brojevi runtime DOM instanci; petlja može napraviti 61 polje ili više kontrola iz jedne definicije. JS skeniranje je statičko, nije dokaz svake moguće runtime grane.

Svi endpointi imaju opis u funkcionalnoj specifikaciji; sve tabele i kolone su u arhitekturi; UI definicije i JS interakcije su u UX dokumentu; sve testne definicije i prethodni slučajevi su u QA dokumentu. Dodatni JSON/CSV inventari čuvaju pune detalje. `provjere/coverage.json` povezuje inventare s dokumentima; `provjere/reference.json` provjerava source:line raspon; `provjere/linkovi.json` relativne linkove; `SHA256SUMS` integritet svih isporučenih datoteka.

Baza je inicijalizovana na novoj privremenoj putanji i pregledana preko PRAGMA; nema čitanja stvarnih zapisa. Testovi nisu ponovo izvršeni: inventarisani su kod i sačuvani JUnit/logovi. Lokalni bundle i patch provjereni su u zasebnom privremenom Git repozitoriju. U ZIP se radi privatnosti uključuju patch i source archive, bez bundle metapodataka autora.

## Nepoznanice i granice potpunosti

Nije dostupna cijela originalna historija/prilozi, pojedinačna matrica D-001–D-100 niti 366 ankera. Nije dokazano konačno stručno odobrenje privremenih kandidat težina. README historijski sadrži zastarjele statuse (npr. audit/AI/Word QA kao nezavršene); konkretni kod i kasniji dokazi imaju prednost. UI još ima engleske poslovne/tehničke izraze. PostgreSQL DDL/migracija nije pronađena; trenutne PG upite ne treba zamijeniti izmišljenom šemom.

SQLite „notnull=0” na nekim tekstualnim PK kolonama je stvarni rezultat PRAGMA, ne preporuka za NULL. Kompanijski ID je organizacijska oznaka, ne sigurnosna granica. Tehnički PASS nije potvrda istinitosti ili produkcijska dozvola. Nijedan sačuvani test rezultat ne potvrđuje stvarni AI/Render/PG.

## README za prenos i otvaranje paketa

Glavnih 11 Markdown dokumenata je u korijenu. `inventari/` sadrži JSON/CSV; `prenos/` kumulativni patch, source archive i siguran primjer env-a. `provjere/` sadrži izvještaje provjera i sintetičke metapodatke bez baza. Prvo provjeriti SHA256SUMS, zatim pročitati [Claude handover](CLAUDE_MASTER_HANDOVER.md).

- Git bundle je napravljen i lokalno provjeren, ali nije uključen u ZIP jer izvorni Git commit zadržava identitet autora. Izabrana je dopuštena alternativa: kumulativni patch i source archive bez tih metapodataka.
- `prenos/mevan-paket2.patch` je kumulativna razlika merge osnove i lokalnog commita. Primjena patcha može dati isto stablo izmijenjenih izvora, ali **ne isti commit SHA**.
- `prenos/mevan-source-132ef28.tar.gz` nastao je `git archive` navedenog commita, bez `.git`, baza, venv-a i nepraćenih datoteka. Jedini namjerno izostavljeni praćeni fajl je `.env.example`, jer sadrži stvarnu administratorsku e-mail adresu. Umjesto njega je zaseban anonimizirani `prenos/config.env.example`. Aplikacijski kod nije redigovan. Zato archive nije doslovna potpuna Git tree kopija; originalni SHA ostaje dokaz porijekla, a jednakost izvora potvrđuju patch tree i hashovi arhive.
- Nema migracije podataka, ključeva, deploy hooka ili slanja Claudeu. Korisnik sam bira lokalni prenos.

Mehanizam isporuke: ovaj executor ima lokalne datoteke i terminal, ali nema pozivljiv `attach_artifact`/upload/file-output alat. `download_file` samo preuzima korisnički prilog. `/codex/.../output` i `/mnt/data` nisu prisutni i korijen OS-a nije upisiv za agent korisnika. ZIP se čuva lokalno. Nije pokrenut HTTP server niti je izvorni kod objavljen na javnom servisu. Provjeren je i dokumentni konektor, koji nema povezanih sesija. Standardni sandbox prilog u ovom executor-u nije potvrđen kao podržan izlazni mehanizam; ne izmišljati download URL. Ako se ne pojavi podržani file output, predaja korisniku ostaje otvorena dok se ne odabere siguran način prenosa.

## Završni rezultat provjera dokumentacije

Svih 11 traženih Markdown datoteka postoji i ima provenance blok. Pokrivenost je 45/45 API ugovora, 11/11 tabela uključujući internu sqlite_sequence, 61/61 kriterij, 217/217 definicija kontrola, 195/195 JS unosa, 125/125 definicija testova i 168/168 prethodnih testnih slučajeva. Provjereno je 866 source:line navoda i 38 relativnih linkova, bez neispravnih odredišta. To su strukturne provjere dokumentacije, a ne novo pokretanje aplikacijskih testova ili dokaz svake runtime grane.

Pročitani su narativni dijelovi svih dokumenata. Zbijeni QA i Claude odlomci preoblikovani su u pune rečenice, poslovni obračuni imaju numeričke primjere, a svih 125 testnih definicija ima zaseban bosanski opis svrhe. Tehnički identifikatori i citirani izvorni assert izrazi ostaju neprevedeni radi preciznosti. `provjere/citljivost.json` bilježi eksplicitnu provjeru ranije spojenih riječi i Markdown ograda.

Privatnosni pregled obuhvatio je tekstove, inventare, patch i raspakovani source archive. Nema pronađenih stvarnih ključeva, ličnih e-mail adresa, deploy hooka ili baza u isporuci. Negativni test URL-a u izvoru ima namjerno sintetički nevažeći credential URL; taj poznati testni obrazac naveden je kao izuzetak, a ne stvarna tajna. Ovo nije opći DLP certifikat.

ZIP i SHA-256 manifest su pripremljeni lokalno. Predaja kroz chat još nije potvrđena: u ovom runtime-u nije dostupan opći izlazni file/upload alat niti povezana dokumentna sesija. Nije pokrenut HTTP server i nije objavljen privatni kod. Korisnik treba odabrati podržani sigurni kanal prenosa; ovaj dokument ne predstavlja lokalnu putanju kao download link.
