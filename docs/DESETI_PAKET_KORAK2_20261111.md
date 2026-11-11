# Deseti paket, korak 2 — 11.11.2026. (tekstovi na ekranima i zaključani izvještaji na engleskom)

Osnova: korak 1. Poslovna logika, podaci i API nisu mijenjani. Na bosanskom se ništa ne mijenja.

## Šta je novo

1. **Objašnjenja, upozorenja i poruke na ekranima** su prevedeni: rječnik `mevan_i18n.py` sada ima 500+ natpisa (ranije 308).
2. **Tekstovi s brojevima** („12 potvrđenih / 12 primjenjivih kriterija”, „Kriterij 1 od 12”, „Indeks 38.3 / 100”, status AI servisa i sl.) prevode se preko obrazaca (`PATTERNS`).
3. **Poruke s detaljem** („AI postavke nisu sačuvane: …”) prevode se do dvotačke; detalj koji dolazi sa servera ostaje kakav jeste.
4. **DEMO traka i status sinhronizacije** su na odabranom jeziku.
5. **Zaključani izvještaji (Direktorski i Detaljni, PDF i Word)** imaju fiksne natpise na odabranom jeziku: naslovi poglavlja, podaci o snimku, nazivi oblasti, periodi plana, zaglavlje, podnožje i broj strane. Jezik je onaj odabran u aplikaciji; adresa preuzimanja prima i `?lang=en` ili `?lang=bs`.

## Šta se u izvještaju ne prevodi

Sve što je zaključano u snimku: sažetak, prioriteti i plan konsultanta, dokazi, nalazi, nazivi kriterija i napomene obračuna. Brojevi, obračun i SHA-256 snimka su isti na oba jezika.

## Šta je još na bosanskom

- Katalog od 61 kriterija (pitanja, dokazi, KPI, preporuke) — korak 3.
- Poruke o greškama koje šalje server (dio iza dvotačke).
- Word izvoz sa stranice „Izvještaji”, Word izvoz integrisane analize i izvještaj projekta.
- Pojedini rjeđi tekstovi na ekranima Projekti i Vođeno prikupljanje koji se sastavljaju iz više dijelova.

## Provjere

- `pytest`: 235 prolaza (231 raniji + 4 nova): obrasci i njihovi dijelovi, isti parametri u šablonima, te zaključani izvještaj kroz stvarni tok odobrenja u PDF i Word obliku — engleski natpisi, isti tekst konsultanta, izbor jezika kroz parametar i kroz kolačić.
- Browser prolaz na engleskom kroz osam stranica dijagnostike: bez JavaScript grešaka; od bosanskog teksta ostaje samo sadržaj kataloga kriterija.
- Oba mobilna toka (na bosanskom) i Word QA 12/12 prolaze.

## Granice

Engleski prevod nije pregledao izvorni govornik ni stručnjak za metodologiju. Provjereno u Chromiumu. Render nije testiran.
