# Osmi paket — 11.11.2026. (isti izgled preostalih izvještaja, prijavljeni korisnik u zaglavlju)

Osnova: sedmi paket. Mijenja se samo izgled. Sadržaj izvještaja, obračuni, API i baza nisu mijenjani.

## Šta je promijenjeno

1. **Izvještaj projekta (PDF i Word)** ima isti izgled kao zaključani izvještaji: zaglavlje i podnožje s brojem strane, naslovni blok, numerisana poglavlja, natpis podatka iznad vrijednosti.
2. **Word izvoz sa stranice „Izvještaji”** („Word · sažetak”, „Word · detaljno”, svih 12 dokumenata) i **Word izvoz integrisane analize** koriste zajedničke stilove: serifni naslovi, tabele s tankim linijama umjesto obojenih polja, zaglavlje „MEVAN DIAGNOSTIC”, podnožje s oznakom DEMO / radni nacrt i brojem strane. Oba izvoza sada grade dokument istom funkcijom (`docxEntries`, `docxTable` u `index.html`).
3. **Prijavljeni korisnik je u vrhu svakog ekrana** (desno u zaglavlju; na telefonu skraćeno).
4. Rezervni font se sada određuje u `mevan_report_fonts.py`; `project_reports.FONT` i dalje postoji.

## Šta nije mijenjano

Tekstovi svih izvještaja su isti. Nazivi datoteka pri preuzimanju su isti. Izbor jezika i unos API ključa nisu dio ovog paketa.

## Provjere

- `pytest`: 208 prolaza (203 ranija + 5 novih u `tests/test_package8_reports_and_user.py`).
- Word QA 12/12; svi dijelovi svakog dokumenta su ispravan XML i otvaraju se kroz python-docx.
- Oba mobilna browser toka prolaze (uključuju preuzimanje i čitanje Word izvoza sa stranice „Izvještaji”).
- Word izvoz integrisane analize preuzet je u stvarnom Chromiumu (oba dugmeta), otvoren kroz python-docx i pretvoren u PDF kroz LibreOffice.
- Vizuelno pregledano kroz LibreOffice: izvještaj projekta (PDF i Word), ukupni sažetak i detaljni izvještaj modula.

## Granice

Word dokumenti nisu otvoreni u Microsoft Wordu, samo u LibreOfficeu. Novi dijelovi dokumenta (zaglavlje, podnožje, veze) prate Word shemu, ali to u Wordu treba potvrditi otvaranjem jednog izvoza. Render nije testiran.
