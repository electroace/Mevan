# Drugi paket — N/P, DEMO i vođeno prikupljanje

Datum: 10.11.2026. Osnova: spojeni PR #1, `be879956ea6ebdc7fc4106459080d3ae85c6202c` na `mevan-v2-test`. Nova lokalna grana: `implementation/mevan-paket-2-20261110`. Izvor odobrenja je izričita korisnička poruka „Korisnik je odobrio DRUGI PAKET implementacije”. Ovo je dopuna ranijeg registra, čiji historijski statusi ostaju sačuvani.

## Dopuna registra zahtjeva i odluka

| Zahtjev | Izvor i status odobrenja | Kod/dokument | Dokaz testa | Preostalo | Kriterij prihvatanja |
|---|---|---|---|---|---|
| R-18: opravdan N/P, konsultant, izuzimanje iz obračuna | Sada izričita odluka korisnika, paket 2; ranije samo prijedlog | `data_quality_gate.py`, `mevan_report_gate.py`, `mevan_report_model.py`, `approved_reports.py`, `index.html` | `tests/test_package2.py`: pet praznih/besmislenih N/P slučajeva; sedam kombinacija modula/miješanog/praznog skupa, četiri izvoza; neprovjereni primjenjivi kriteriji blokirani | Stručna istinitost razloga nije automatizovana | Samo primjenjivi kriteriji u nazivniku; prazan skup `None`/„Neocjenjivo”; razlog i konsultant vidljivi u oba izvještaja |
| R-19: trajna DEMO oznaka | Sada izričita odluka korisnika, paket 2, tačan tekst oznake | Vezani snimak v2, manifest, API i oba renderera; projektni režim | Četiri izvoza, PDF svaka stranica, DOCX zaglavlje/podnožje; promjena URL-a nema uticaja; simulacija ne dobija stvarno odobrenje | Stvarna provjera podataka zahtijeva nezavisan rad konsultanta | „DEMO — simulirani podaci” ostaje vezano za snimak; DEMO nema potvrđene finansijske tvrdnje ni odobrenje implementacije |
| R-11: vođeno prikupljanje do 90 dana | Izričita odluka korisnika, potvrđena opsegom paketa 2 | `diagnostic_review.html`, `mevan_sync_guard.py`, postojeći projektni API i `index.html` | `browser_package2.py`: intervju → dokumenti → obilazak → dokazi/N/P → prioriteti → C2 nacrt → plan; osvježavanje i povratak; test zamrznutog snimka i restorea | Izvori su tekstualne bilješke/reference; nema novog uploada datoteka | 61 kriterij/5 modula; odvojeni izvori i nedostaci; trajno čuvanje s kontrolom revizije; vlasnik/KPI i tri roka projektnog nacrta |
| R-08/R-28: očuvati C1/C2/C3 | Izričita odluka da se težine ne mijenjaju; ranije metodološko odobrenje težina i dalje nepoznato | `project_planner.py` i rangiranje ostaju neizmijenjeni | Postojeće regresije i mobilni tok: C1 81, C3 72, C2 67 | Stručna kalibracija izvan opsega | Isti primjenjivi ulaz daje isti poredak; izbor prioritetnog nacrta ne mijenja rangiranje |
| R-14/R-04: historijska odobrenja i rezultati | Izričito očuvanje u paketu 2 | Čitač snimka v1/v2; verzionisani gate i zamrznuti model | Historijski v1 s kratkim sažetkom čitljiv u četiri izvoza; naknadni rad ne mijenja v2 izvještaj | Historijski v1 koristi postojeći obračunski put, bez retroaktivnog prepisivanja | Nema migracije, prepravljanja historijskih snimaka ili starih rezultata |
| R-26/R-27: D-001–D-100 i CSV ankera | Nepoznato; izvor nije pronađen ni u ovom pregledu | Postojeći dokumenti imaju grupne opise | Nije moguće dokazati pojedinačnu pokrivenost nedostupne matrice | Pribaviti originalni izvor/verziju | Bez izmišljanja pojedinačnih zahtjeva ili pripisivanja odobrenja |

## Pravila i kompatibilnost

Novi N/P razlog mora imati najmanje 20 znakova, četiri riječi i tri različite riječi; ponovljene zamjenske riječi nisu dovoljne. Potrebno je ime konsultanta, ocjena mora biti prazna. To je tehnička provjera potpunosti, ne stručna ocjena opravdanosti. Eksplicitni pregled kritičnih rizika O14/L09/M08 ostaje obavezan i kod N/P. Za primjenjive stvarne kriterije ostaju postojeći provjereni dokazi i metapodaci; samoprocjena/neprovjereni dokumenti/simulacija ne prolaze stvarni gate.

Novi zaključani snimak v2 sadrži režim i zamrznuti obračunski rezultat u istom hashom zaštićenom JSON-u. Manifest i preuzimanje čitaju taj režim; URL parametar ga ne bira. Historijski v1 ostaje na ranijem čitaču i pravilima. Nema promjene SQL šeme ni produkcijske migracije. N/P se izuzima iz ukupnog i modularnih prosjeka. Radar koristi zamrznute indekse; ako neka oblast nema primjenjivih ocjena, radar se izostavlja s obrazloženjem umjesto crtanja nule.

DEMO zahtijeva eksplicitan izbor, simulirane primjenjive zapise i dokazne reference. Pripremljeni METALPRO primjer dopunjava prazne bilješke i pregled, jasno označen kao simulacija. Nema nezavisno potvrđenih finansijskih tvrdnji. DEMO projektni nacrt zadržava režim, ne može se preimenovati u stvarni niti dobiti implementacijsko odobrenje. Vođeni tok ne povezuje postojeći projekat drugog režima. Stari radni izvozi i pregled za štampu također prenose oznaku i razloge N/P; oni ostaju nacrti.

Vođeni tok koristi postojeći TEST workspace s kontrolom revizija. Intervju, dokumenti i obilazak su zasebne bilješke po kriteriju. Spremanje i osvježavanje ne brišu pregled; promijenjeni ulaz zahtijeva potvrdu i poništava provjeru promijenjenog kriterija. Povratak na glavni ekran prikazuje pregled samo ako se izvorne ocjene podudaraju. Projektni nacrt koristi postojeći API, izabrani prioritet, vlasnika, KPI i aktivnosti do 30/60/90 dana; osnovica, ciljevi i implementacija nisu automatski odobreni. C1/C2/C3 izbor u ovom koraku označava prvi/drugi/treći uneseni prioritet, a ne promjenu postojećeg algoritma rangiranja kandidata.

## Provjera i ograničenja

- Postojeći paket prije novih regresija: 136 prolaza. Zajedno s 32 nove regresije: **168 prolaza**, jedno postojeće upozorenje Starlette/httpx.
- Word QA: **12/12**, provjera ZIP/XML i sadržaja. Postojeće provjere nisu uklonjene.
- Mobilni Chromium 390 × 844: oba paketa prolaze; paket 1 ponovljeni 4.000 KM ostaje jedan efekat, zaseban događaj očuvan, sedam `x` odbijeno, valjan bosanski primjer prihvaćen, stale revizija odbijena. Paket 2 čuva izvore/N/P/projekat/plan i četiri DEMO izvoza. Dodatna ciljana provjera pokriva stari pregled za štampu i Word nacrt.
- PDF uzorci vizuelno pregledani: naslov/DEMO podnožje, radar i N/P razlozi, detaljni izvori. DOCX su strukturno i sadržajno provjereni; nema instaliranog Word/LibreOffice renderera za vizuelnu paginaciju DOCX.
- Samo sintetičke privremene SQLite baze. Stvarni AI, Render, udaljeni PostgreSQL, produkcijski podaci i hosting nisu testirani. Novi CI nije pokrenut jer nema pusha. Bez promjene workflowa, težina, main/base upisa, deploya ili Render postavki.
- Nema dostupne dokument/PDF vještine u katalogu ovog okruženja; korišteni su postojeći Word QA, python-docx, ReportLab i Poppler. Vanjski prilozi ostaju izvan potvrđenog obuhvata restorea: test vraća SQLite sadržaj, uključujući audit redove i nove JSON bilješke/snimke, ali ne dokazuje vraćanje vanjskih datoteka.

Detaljni logovi, slike, PDF/DOCX uzorci, diff i kontrolni hashovi čuvaju se uz prethodnu analizu u `work/mevan-analysis/paket-2/` izvan repozitorija. Raniji izvještaji su historijski dokazi; ovaj dokument ne mijenja njihove tadašnje rezultate ili statuse odobrenja.
