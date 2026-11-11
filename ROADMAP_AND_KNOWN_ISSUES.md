> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: stanje implementacije, dug i otvorene odluke, bez novog odobrenja promjena.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — plan nastavka, poznata ograničenja i otvorene odluke

## Kako čitati statuse

„Implementirano/lokalno provjereno” znači kod i navedeni sintetički dokaz na `132ef28`. „Djelimično” znači postoji upotrebljiv podskup ili paralelni stari put. „Neimplementirano” znači nema rute/modela/ekrana u pregledanom kodu. „Neprovjereno” znači nema odgovarajućeg izvršenog dokaza. „Preporuka/planirano” nije odobrenje implementacije. Nijedan status ovdje ne znači da je paket 2 objavljen na Renderu.

## Lokalno, GitHub i hosting su tri različita stanja

| Površina | Zabilježena verzija | Dokaz / granica |
|---|---|---|
| Lokalni kod | `132ef288917b0573709655437cb8904574898015` | Ponovo read-only potvrđeni HEAD/status u ovom zadatku; paket 2 |
| GitHub `mevan-v2-test` | `be879956ea6ebdc7fc4106459080d3ae85c6202c` | Prethodno potvrđeno spajanje [PR #1](https://github.com/mevan-platform/mevan-diagnostic/pull/1); lokalni remote-tracking ref, bez novog fetch-a |
| Render `mevan-diagnostic-v2-test` | `85fd230eb7d781bb6d25b3e8f1552f8e54f31a2b`, Live; Auto-Deploy Off | Izvorni chat je prijavljeno read-only provjerio dashboard, granu `mevan-v2-test` i [adresu](https://mevan-diagnostic-v2-test.onrender.com); nije nova cloud provjera |

Claude koji samo klonira GitHub **ne dobija paket 2**. Izvori lokalnog commita prenose se patchom na potvrđenu merge osnovu; patch sam ne kreira originalni commit SHA. Nema automatskog deploya iz same predaje; Render postavke se ne mijenjaju.
## Historija, izričite odluke i precedence

Dostupni izvori: korisničke poruke u ovoj niti; `docs/MEVAN_REGISTAR_AKTIVNOSTI_v8.md`; `MEVAN_4_0_KORAK_3_STATUS.md` do postojećeg koraka 23 (nisu sve numeričke datoteke prisutne); `docs/PRVI_PAKET_20261110.md`; `docs/DRUGI_PAKET_20261110.md`; postojeći izvještaji analize izvan repozitorija. Status dokumenta „završeno” nije dokaz da je korisnik odobrio svaku njegovu preporuku.

1. Početno je odobrena samo analiza i plan; izričito je tražen nastavak postojeće aplikacije, 61 kriterij/5 modula, AI, trajni C1/C2/C3, PDF/DOCX, sažetak i 90 dana, vođeno prikupljanje, jednostavniji premium mobilni tok i stabilan PIT demo 3–4.12.2026. Prva verzija samo bosanski; engleski kasnije.
2. Raniji N/P detalji i DEMO režim bili su prijedlozi, bez odobrenja. Kasnije izričito odobren prvi paket obuhvatio je samo idempotentne efekte, tehničku validaciju pregleda i stvarni uzrok pada Word QA. Zatim su zasebno odobreni commit/push/PR, read-only review, CI izmjena i spajanje PR #1, bez deploya.
3. Prvi paket i CI spojeni su u `mevan-v2-test` na `be879956ea6ebdc7fc4106459080d3ae85c6202c`. PR #1 je prema prethodno potvrđenom stanju merged. CI odobrenog heada `2a31e358c1d7c72f79c4acb25907dabd9ba34fb5` završio je uspješno: [Actions 42899507229](https://github.com/mevan-platform/mevan-diagnostic/actions/runs/42899507229). Ovo nisu novi mrežni upiti.
4. Najnovije implementacijsko odobrenje je paket 2 na novoj lokalnoj grani: opravdan N/P s konsultantskom potvrdom i izuzimanjem, eksplicitni trajni DEMO te vođeni tok. Time su R-18/R-19 dobili izričito odobrenje samo u tom opsegu. Nisu promijenjene težine C1/C2/C3. Lokalni commit je `132ef288917b0573709655437cb8904574898015`, bez pusha/PR-a/deploya.
5. Sadašnji zadatak je samo dokumentacija i prenos lokalnog koda. Ne daje novo odobrenje za implementaciju, push, spajanje ili hosting.

Prioritet: posljednja konkretna izričita korisnička odluka za dati opseg > ranija odluka za isti opseg > prijedlog asistenta. Nepotvrđene preporuke (benchmark, stručna kalibracija, konačni dizajn ili budući tenant model) ne postaju odobrene samim postojanjem dokumenta. Nedostupni D-001–D-100 ne mogu se rekonstruisati iz grupnih opisa. CSV 366 ankera nije verifikovan; postoje samo vidljive opće skale i pitanja.

## Registar funkcionalnog stanja i duga

| Oblast | Status | Dokaz u kodu / QA | Preostalo / granica |
|---|---|---|---|
| Postojeća aplikacija, 61/5 | Implementirano, očuvano | index katalog, diagnostic_engine; 61 katalog test | Nedostaju pojedinačna matrica zahtjeva i stručni ankeri |
| Bosanski prvi | Djelimično cijeli stari UI; nove poruke BS | lang=bs, Guided/reports, prevedeni v3 naslovi | Preostali engleski naslovi/termini; ne uvoditi EN fazu |
| N/P opravdan | Implementirano/paket 2 lokalno provjereno | gate v2, report_model, 7 kombinacija/4 formata | Tehnički prag ne dokazuje stručnu opravdanost; kritični pregled rizika ostaje |
| Prazan primjenjivi skup | Implementirano/provjereno | None/Neocjenjivo, radar objašnjenje | Ne prikazivati 0/100 ili zamišljenu sigurnu procjenu |
| DEMO odvajanje | Implementirano/paket 2 lokalno provjereno | mode snapshot/manifest, četiri izvoza/URL, zaštita projekta | Ljudska istinitost ne može se dokazati detektorom teksta |
| Guided tok | Implementiran minimalan BS tok | odvojeni izvori, koraci, trajnost, projekat i plan; mobilni tok | Nema stvarnog document upload-a, redizajna ili offline multi-device mergea |
| C1/C2/C3 trajnost | Implementirano na SQLite-u/provjereno | candidate CAS/weights/ranking 81/72/67 | Udaljeni PG neprovjeren; težine privremena konfiguracija |
| AI | Implementirani endpointi i mock testovi | serverski AI i project_ai_pack | Stvarni model/format/kvalitet/trošak nisu potvrđeni |
| Konsultantski review | Implementirana tehnička validacija | summary/priorities/months, negativni testovi s unosom x, history | Nema automatske stručne ocjene kvaliteta |
| PDF/DOCX | Implementirano više paralelnih puteva | 4 snapshot formata, 12 legacy Word izvještaja, projektni izvozi | DOCX vizuelna paginacija neprovjerena; paralelne šeme/semantika nacrta |
| Idempotentni efekti | Implementirano na SQLite-u/provjereno | canonical/eventkey/UUIDv5/transaction/audit | Preklapajući periodi i stari duplikati nisu automatski riješeni |
| Scenariji/ROI | Implementirano/provjereno | Decimal, tri scenarija, odvojeni WC | Bez NPV-a/diskontovanja; nije billing/PDV niti nezavisno potvrđen rezultat |
| Projekti/status/audit/weeklies | Implementirano, postojeći testovi | Charter, provjera ISO sedmice, čitanje izvoza, audit | Nema close/delete API; neke unutrašnje dict šeme slabe; aktivni projekat SELECT race |
| Dva workspacea | Implementirano paralelno | legacy CAS+TEST revizija+overlay | Nema jedne atomske transakcije ili opće sinhronizacije između njih |
| Backup | Implementirani različiti formati | legacy JSON, TEST snapshot, SQLite WAL restore | Nema offsite/enkripcije/schedule/PG+prilozi punog restorea |
| Korisnici/tenant/RLS | Neimplementirano | Jedan env administrator, bez users tabele/ACL | Potrebna odluka instance vs multi-tenant prije stvarnih više klijenata |
| Billing/pretplate/cijene/PDV/CRM/artikli | Neimplementirano/N/A | Nema tabela/ruta/modela | Ne dodavati generičke SaaS zahtjeve bez odluke |
| Security hardening | Djelimično | Session/origin/token/limits/headers | Nema potpunog pentesta, MFA, revokacije, WORM, distribuiranog limiter-a |
| CI prvi paket | Uspješan prethodni run | Actions 42899507229: 136+Word 12+Chromium | Novi lokalni Guided browser nije workflow step; paket 2 nije pushan |
| Hosting/deploy paketa 2 | Nije objavljeno | Lokalni commit bez remote mutacija | Nema odobrenja za push/PR/deploy u ovom zadatku |
| PIT demo | Lokalni sintetički tok provjeren | METALPRO/mobile/exports | Generalna proba živog odobrenog okruženja i rezerva tek po posebnom dogovoru |

## Konkretne tehničke nepoznanice, bez usputne implementacije

1. PG tabela nema pronađen CREATE/migraciju; kod pretpostavlja konfliktni ključ i JSON payload. Ne navoditi remote tipove/RLS kao potvrđene. Ako se PG aktivira, prvo read-only inventar odobrene testne šeme i zaseban backup plan.
2. Projekat može biti kreiran/implementiran kroz vlastiti API bez provjere formalnog approved diagnostic snapshot ID-a; tri bool flag-a su izjave konsultanta. Potrebna stručna/procesna odluka prije eventualne strože veze, bez retroaktivnog zaključavanja starih projekata.
3. Aktivni projekat je SELECT provjera bez SQL jedinstvenosti; statusne tranzicije nisu sve očekivana-revizija CAS. To je potencijalna konkurentna slabost koja ovim dokumentovanjem nije repro-testirana ili promijenjena.
4. Neki `FinancialModel.model_validate` pozivi u dict handlerima nisu uhvaćeni u HTTPException 422, pa nedozvoljeni ručni ulazi mogu završiti kao 500. To je nalaz statičkog čitanja, ne novi izvršeni incident ili opravdanje za izmjenu sada.
5. V3 prompt i normalizacija imaju slabije tačke: `str(item.get('score') or '')` može tekstualnu nulu prevesti u prazan unos za AI context ako je score numerički 0; backend facts ostaju iz deterministic enginea. Semantička provjera formula/hipoteza nije kompletan evaluator. Ne tvrditi da svaki prompt zahtjev ima server validator.
6. Guided projekat koristi due_date/phase/title, stari structured UI ima deadline/title i planner name/due; izvještaji imaju fallbackove ali nema jedne stroge šeme svih list dict elemenata. Dalje usklađivanje zahtijeva kompatibilan plan, bez gubitka starih ključeva.
7. Snapshot v2 zamrzava obračun, ali tekstualni renderer/katalog/formati još zavise od budućeg koda. Zamrznuti model čuva brojke, ne arhivira završne PDF/DOCX bajtove. Potpuna byte-for-byte dugoročna reprodukcija zahtijevala bi dodatnu arhivu/renderer verziju; nije implementirana.
8. Hash snimka je kontrola integriteta, ne nezavisni potpis; reviewer/time su DB metadata. Tabele/audit nisu WORM, nema kriptografskog lanca događaja.
9. Instalacije rasponskih dependencies i image tag nisu potpuno reproducibilne bez lock-a/digest-a. Nova dokumentacija daje installed verzije, ne tvrdi da je lock dodan.
10. Source archive izostavlja .env.example radi privatnosti; patch prenosi isto stablo izvora na bazni commit; originalni commit SHA se time ne rekreira. Nema stvarnih podataka u predaji; ne zamijeniti source handover migracijom baze.

## Minimalan naredni plan, uz postojeće granice

**Odmah, dokumentacijska predaja:** provjeriti manifest, merge osnovu i stablo izvora nakon patcha, čitati 11 dokumenata, držati novi radni branch lokalno. Ne deployati i ne mijenjati baznu granu. Ovaj korak je odobren sada.

**Prije nove implementacije:** dogovoriti konkretan sljedeći paket, odvojiti produkcijsku sigurnost od funkcionalnog demo završetka, pribaviti nedostupnu matricu/ankere ako postoje. Odobrene završene dijelove ne otvarati ponovo bez konkretne regresije. N/P i DEMO više nisu samo prijedlog; njihov obuhvat je tačno paket 2. Težine i sve druge neodobrene metodološke promjene ostaju van opsega.

**Prije budućeg odobrenog PR-a:** provjeriti bazu/head/remote promjene bez prepisivanja tuđeg rada; razmotriti ciljanu CI dopunu za novi Guided browser, rerun samo relevantan nakon novih izmjena; napraviti review diffa i sintetičkih dokaza. Push/PR nisu odobreni ovom dokumentacijom.

**Prije stvarnog klijentskog korištenja:** zaseban sigurnosni plan i autorizacija/tenant model, provjeren backup svih aktivnih skladišta, stvarni AI test na dopuštenim sintetičkim podacima, vizuelni Word pregled, hosting trajnost/TLS i generalna proba. Render Auto-Deploy Off mora se očuvati dok korisnik izričito ne odobri drugačije. Ni merge PR-a nije implicitna dozvola ručnog deploya.

Otvorene odluke: konačne težine/stručni ankeri; model jednog ili više klijenata; dokazni dokumenti i trajno skladištenje; pravila audit retention/enkripcije; prihvatljiv stvarni AI model/budžet; konkretan sljedeći implementacijski opseg. Za rutinski nastavak dokumentacije ova pitanja nisu blokada.
