# Deseti paket, korak 1 — 11.11.2026. (izbor jezika, engleski meni i fiksni natpisi)

Osnova: deveti paket. Poslovna logika, podaci, API i izvještaji nisu mijenjani. Bosanski je i dalje zadani jezik i u njemu se ništa ne mijenja.

## Šta je novo

1. **Izbor jezika u zaglavlju (BS / EN)** na svakom ekranu i na stranici za prijavu. Izbor se pamti godinu dana (kolačić `mevan_lang`) i vrijedi za sve ekrane. Promjena jezika ostaje na istoj stranici.
2. **Na engleskom su:** meni, zaglavlje, „Odjava”, prijava (i poruka o pogrešnoj prijavi), prozori za potvrdu i unos, te fiksni natpisi na sva četiri ekrana: dugmad, naslovi, natpisi polja i izbori u padajućim listama (308 natpisa).
3. **Jedan rječnik:** `mevan_i18n.py`. Ključ je izvorni bosanski tekst, vrijednost engleski. Tekst bez prevoda ostaje na bosanskom, pa se prevod dopunjava dodavanjem redova u rječnik, bez izmjene stranica.
4. **Kako radi:** server ispisuje meni i zaglavlje na odabranom jeziku; zajednička skripta u `mevan_nav.py` prevodi fiksne natpise čim se pojave na stranici.

## Šta se ne prevodi

- Tekst koji unese korisnik: polja za unos i veći tekst se ne diraju, a nazivi kompanije, dijagnostike, projekta i finansijskog nalaza imaju oznaku `translate="no"`.
- Podaci koji se šalju serveru ostaju isti na oba jezika (vrijednosti izbora se ne mijenjaju).

## Šta je još na bosanskom (naredni koraci)

- **Korak 2:** objašnjenja i upozorenja na ekranima, poruke sa servera, sastavljeni tekstovi s brojevima („12 potvrđenih / 12 primjenjivih kriterija”, „Kriterij 1 od 12”), DEMO traka, te fiksni natpisi u izvještajima (PDF i Word).
- **Korak 3:** katalog od 61 kriterija (pitanja, dokazi, KPI, preporuke) i pravila ocjenjivanja; prevod treba stručni pregled.

Do tada je engleski prikaz mješovit: okvir i natpisi su na engleskom, a sadržaj i izvještaji na bosanskom.

## Poznato ograničenje

Ako korisnik unese kratak tekst koji je isti kao neki natpis iz rječnika (npr. aktivnost s nazivom „Status”) i taj tekst se prikaže izvan polja za unos i izvan označenih naziva, na engleskom će biti prikazan preveden. Sačuvani podatak se ne mijenja.

## Provjere

- `pytest`: 231 prolaz (224 ranija + 7 novih u `tests/test_package10_language.py`): zadani jezik, pamćenje izbora na sva četiri ekrana, odbijanje nepoznatog jezika i tuđe povratne adrese, prijava, svaki ključ rječnika postoji u interfejsu, zaštita korisničkog sadržaja.
- Browser prolaz na 1366 px i 390 px na engleskom: prijava, pogrešna prijava, svih pet stranica dijagnostike i tri ostala ekrana bez horizontalnog pomjeranja i bez JavaScript grešaka; prozor za unos; kompanija s nazivom „Finansije” ostaje „Finansije”; povratak na bosanski na istoj stranici.
- Oba mobilna toka (na bosanskom) i Word QA 12/12 prolaze.

## Granice

Engleski prevod natpisa nije pregledao izvorni govornik ni stručnjak za metodologiju. Provjereno u Chromiumu. Render nije testiran.
