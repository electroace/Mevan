# Šesti paket — 11.11.2026. (pristupačnost i ujednačen izgled)

Osnova: četvrti paket s dugmadima (commit „Paket 5: jedinstvena dugmad”). Mijenja se samo izgled, raspored i način prikaza poruka. Poslovna logika, API, baza, obračuni i izvještaji nisu mijenjani.

## Šta je promijenjeno

1. **Natpisi su povezani s poljima.** Svaki vidljivi natpis sada pripada polju ispod sebe (čitač ekrana ga čita, klik na natpis otvara polje). Radi na sva četiri ekrana; povezivanje je na jednom mjestu, u `mevan_nav.py`.
2. **Sivi pomoćni tekst je tamniji** (`#566b7c`, kontrast najmanje 5,0 na svim podlogama; ranije 3,9–4,3).
3. **Pregled: traka pokazuje indeks zrelosti**, a ne popunjenost. Popunjenost („12 potvrđenih / 12 primjenjivih”) ostaje kao tekst. U modulu traka i dalje pokazuje potvrđene kriterije, sada s natpisom „12/12 potvrđeno”.
4. **Jedan izgled na sva četiri ekrana.** Boje, širina sadržaja, kartice, polja, naslovi i veličina brojki definisani su jednom, kao CSS varijable u `mevan_nav.py`. Sadržaj svuda koristi punu širinu pored menija.
5. **Manje žutih upozorenja.** Stalna DEMO traka ostaje. Tri opće napomene (Kompanije i dijagnostike, Analiza i odobravanje, Izvještaji) sada su obične napomene; tekst je isti. Upozorenja vezana za konkretan sadržaj (finansijske hipoteze, AI nacrt, DEMO na Projektima) ostaju žuta.
6. **Registar finansijskih efekata:** svaki nalaz je red sa sažetkom (naziv, iznos, vrsta i status) koji se otvara klikom. Otvoreni red ostaje otvoren nakon izmjene polja. Novi nalaz se odmah otvara.
7. **Poruke i potvrde su u aplikaciji**, ne u sistemskim prozorima preglednika. Obavijesti se pojavljuju na dnu ekrana (greške ostaju dok se ne zatvore), a potvrde i unos naziva u prozoru aplikacije. Sve ranije potvrde postoje i dalje, s istim tekstom, uključujući upis „VRATI-PODATKE”.
8. **Uklanjanje aktivnosti iz Plana 90 dana sada traži potvrdu** (ranije se brisalo odmah).
9. **„Vrati METALPRO simulaciju”** je premješteno iz reda s „+ Nova kompanija” u zaseban dio „Demo podaci” na istoj stranici.
10. **Status sinhronizacije je vidljiv** ispod DEMO trake („Sačuvano na serveru”, „Greška sinhronizacije…”).
11. **Prijava** ima isto zaglavlje i izgled kao aplikacija; pogrešna prijava se prikazuje u obrascu (status 401 je isti).
12. **Projekti:** uz tri onemogućena dugmeta stoji objašnjenje kada postaju aktivna.
13. **Telefon:** sva dugmad, i mala „Ukloni”, visoka su najmanje 44 px.

## Šta nije mijenjano

Nijedna funkcija, naziv dugmeta, `id` ni `data-page` oznaka nisu uklonjeni. Tekstovi upozorenja i potvrda su isti.

## Provjere

- `pytest`: 194 prolaza (186 ranijih + 8 novih u `tests/test_package6_design.py`). U `tests/test_package4_nav.py` izmijenjena su tri reda: provjeravaju iste potvrde, sada kao `mvConfirm`.
- Word QA 12/12.
- Oba mobilna browser toka prolaze (`browser_approved_smoke.py`, `browser_package2.py`); u njima je izmijenjen samo način prihvatanja potvrde.
- axe-core na 390 px: 0 nalaza na prijavi i 10 ekrana aplikacije (ranije kontrast na svima i do 48 polja bez natpisa po ekranu). Na Vođenom prikupljanju bez odabrane dijagnostike ostaje raniji umjereni nalaz o oznaci glavnog dijela stranice.
- Ručni browser prolaz na 1440 px i 390 px: svi ekrani bez horizontalnog pomjeranja i bez JavaScript grešaka; potvrde (Odustani, Escape, Potvrdi), unos naziva tipkom Enter, obavijesti, otvaranje i izmjena reda u registru.

## Granice

Provjereno u Chromiumu. Safari i Firefox nisu testirani. Stvarni AI, Render i udaljeni PostgreSQL nisu testirani. `browser_smoke.py` nije pokrenut jer traži Chromium na `/usr/bin/chromium`; iste rute su provjerene ručnim prolazom. Pojedinačne boje unutar stranica (oko 50 vrijednosti) nisu sve zamijenjene varijablama; zajednička pravila ih nadjačavaju tamo gdje se razlikuju.

## Dopuna 6.1 — dugme „Odjava”

**Greška:** klik na „Odjava” u meniju vraćao je `{"detail":"Nedozvoljen izvor"}`. Uzrok: zbog zaglavlja `Referrer-Policy: no-referrer` preglednik šalje obrazac s `Origin: null`, a server je tražio tačan izvor. Greška postoji otkako je odjava obrazac u zajedničkom meniju (četvrti paket); raniji testovi su slali ispravan `Origin` i nisu je uhvatili.

**Popravka:** obrazac za odjavu nosi potpisani token vezan za trenutnu sesiju, kao obrazac za prijavu. Server prihvata odjavu ako je izvor ispravan ili ako je token ispravan. Sigurnosna zaglavlja nisu mijenjana.

**Provjere:** `pytest` 196 prolaza (dva nova: odjava s `Origin: null` i tokenom uspijeva; bez tokena, s pogrešnim tokenom ili s tuđim izvorom i dalje se odbija). Odjava kliknuta u stvarnom Chromiumu vodi na prijavu. Oba mobilna toka i Word QA 12/12 prolaze.
