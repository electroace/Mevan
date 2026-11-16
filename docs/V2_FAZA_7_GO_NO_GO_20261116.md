# Integracija 65/6 — faza 7 (16.11.2026.): završni test i preporuka GO / NO-GO

Grana: `mevan-v2-test`. Ništa nije objavljeno na produkciju: grana `main` i servis `mevan-test` nisu dirani tokom cijele integracije.

## Preporuka

- **GO za testni Render servis `mevan-v2-test`:** model 65/6 se može koristiti za internu provjeru na simulacijama i za pregled s vlasnikom metodologije.
- **NO-GO za produkciju** (spajanje u `main`, rad sa stvarnim klijentom) dok se ne ispune uslovi navedeni na kraju dokumenta.

## Stvarni rezultati testova

| Provjera | Rezultat |
|---|---|
| `pytest`, cijeli repozitorij | 381 prolaz, 0 padova |
| od toga testovi integracije 65/6 (faze 0–7) | 129 |
| Referentni testovi iz paketa (`build_mevan_v12.py`) | 26/26; svi scenariji su preneseni na stvarni kod |
| Mobilni browser tokovi za 61/5 (dva postojeća) | prolaze |
| Word QA za 61/5 | 12/12 |
| Završni browser prolaz 65/6, desktop 1366 px i telefon 390 px | prolazi, bez JavaScript grešaka i bez horizontalnog pomjeranja |
| Testni Render servis | `/health` odgovara; funkcije na Renderu nisu testirane iz razvojnog okruženja |

## Tri simulacije, kroz API od početka do kraja

Ocjene su iz `MEVAN_TRI_KOMPANIJE_65_OCJENA.csv`. Sve tri nose oznaku simulacije.

| | METALNOVA | TEKSTILORA | DRVONOVA |
|---|---|---|---|
| Kriterija | 65 | 65 | 65 |
| Indeks zrelosti (engine) | 42,2 | 43,4 | 36,6 |
| Isto, ručno iz ocjena | 42,2 | 43,4 | 36,6 |
| Indeksi šest modula | jednaki ručnom obračunu | jednaki | jednaki; isti kao u referentnom PDF-u |
| Potvrđeni uzroci | 0 | 0 | 0 |
| Potvrđeni finansijski efekti | 0 KM u sve četiri kolone | 0 KM | 0 KM |
| Hipotetički potencijal (isti ogledni efekti) | 136.000 KM/god i 195.000 KM jednokratno | isto | isto |
| Efekat na kriteriju bez modela | blokiran | blokiran | blokiran |
| Indeks pouzdanosti | nepoznat (izvori nisu ocijenjeni) | nepoznat | nepoznat |
| Rang tri opcije | 90,0 / 77,0 / 50,0, konačan | isto | isto |
| Premium PDF | 17 strana, oznaka simulacije na svakoj | 17 | 17 |

Za svaku kompaniju je provjereno i da dijagnostika 61/5 u istom radnom prostoru ostaje bez oznake verzije i da dnevnik sadrži svih pet vrsta događaja.

## Kontrolni slučaj na podacima koji nisu simulacija

Simulacija po pravilu ne može ništa potvrditi, pa su putanje potvrde provjerene zasebno, istim ulazima bez oznake simulacije:

- Uzrok je potvrđen samo na kriteriju gdje su ispunjena sva četiri uslova; susjedni kriterij ostaje hipoteza.
- OEE i SMED na istom ključu: drugi je blokiran.
- OEE i OTIF iz različitih porodica na istoj lokaciji, periodu i nalogu: oba blokirana; nakon pisanog obrazloženja nezavisnosti oba su priznata (116.000 KM/god).
- Zalihe ostaju u koloni jednokratne gotovine (195.000 KM); ukupnog zbira nema.
- Indeks pouzdanosti se izračuna i jednak je ručnom obračunu; indeks zrelosti ostaje 42,2.

## METALPRO DEMO i model 61/5

Nepromijenjeni: 61/61 kriterija, indeks 36,4, indeksi dimenzija, 0 KM potvrđenih efekata, kandidati C1–C3 i struktura Word izvještaja. To potvrđuju zaključani otisak iz faze 0 (prolazi u svakoj fazi), poseban test u ovoj fazi i browser prolaz, u kojem METALPRO nakon rada s dijagnostikom 65/6 i dalje prikazuje 61/61 i 36,4.

## Greške nađene u ovoj fazi

1. **Stranica „Izvještaji” na telefonu se širila izvan ekrana** kad je vrijednost u kutiji duga (npr. „Nije procijenjeno”). Javlja se za svaku dijagnostiku koja nije METALPRO, u oba modela. Ispravljeno u zajedničkom stilu; dodan test.
2. **Dvije pogrešne očekivane vrijednosti u samom testu** (rezultat ranga i finansijska sljedivost). Engine je bio u pravu; očekivanja su ispravljena nakon ručnog obračuna, koji je upisan uz test.

Ranije u integraciji nađeno i ispravljeno: oznaka nacrta metodologije za pregled za štampu bila je na pogrešnom mjestu (faza 1c).

## Preostali rizici

**Metodologija i pravila (odluke vlasnika):**
- Svih 65 mapiranja kriterij → finansijski model u izvoru čeka stručnu potvrdu.
- Obračun pet komponenti pouzdanosti je radno pravilo implementacije; specifikacija ga ne propisuje.
- Četvrta finansijska kolona (očekivana vrijednost rizika) je odstupanje od prototipa koje nije potvrđeno.
- Pragovi i ponderi pouzdanosti su privremeni i nisu kalibrisani.

**Funkcije koje za 65/6 ne postoje:**
- Postupak odobrenja i zaključavanja izvještaja; premium PDF zato uvijek nosi „NEODOBRENO”.
- AI analiza, AI nacrt i Vođeno prikupljanje.
- Engleski jezik za ekrane 65/6, katalog 65 kriterija i premium PDF.
- Dokaz kao zaseban zapis (izvor, period, vlasnik, otisak dokumenta); dokaz je tekst uz kriterij.
- Veze između kriterija; uzročna strana prikazuje jedan nalaz.
- Veza finansijskih efekata na stvarne transakcije; preklapanje se prepoznaje po ključu koji unese konsultant.
- Ekran „Projekti” (charter, sedmični pregledi) za opcije 65/6.

**Okruženje:**
- Besplatni Render servis nema trajni disk: baza, AI ključ i evidencija potrošnje se brišu pri svakom deployu.
- Testirano samo u Chromiumu; Word dokumenti nisu otvoreni u Microsoft Wordu.
- Aplikacija je i dalje prototip s jednim nalogom i bez produkcijske sigurnosne revizije.

## Uslovi za GO na produkciju

1. Vlasnik metodologije potvrdi 65 mapiranja i pravila pouzdanosti (ili ih izmijeni).
2. Postoji odobrenje i zaključavanje izvještaja za 65/6.
3. Podaci su na trajnom disku ili u bazi koja preživljava deploy.
4. Jedna dijagnostika 65/6 je urađena sa stvarnim podacima uz konsultanta, i izvještaj je pregledan.
5. Premium PDF i Word provjereni u programima koje kupac koristi.
