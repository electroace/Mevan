# Deseti paket, korak 3 — 11.11.2026. (katalog kriterija i Word izvozi na engleskom)

Osnova: korak 2. Poslovna logika, obračuni, sačuvani podaci i API nisu mijenjani. Na bosanskom se ništa ne mijenja.

## Šta je novo

1. **Katalog od 61 kriterija na engleskom** (`mevan_criteria_en.py`): naziv, pitanje, dokazi, KPI, preporuka i finansijski aspekt za svaki kriterij. Na engleskom se ti tekstovi zamjenjuju pri učitavanju stranice; šifre (F01…M12) i dimenzije ostaju iste.
2. **Word izvoz sa stranice „Izvještaji”** (svih 12 dokumenata) i **Word izvoz integrisane analize** koriste isti rječnik: naslovi poglavlja, zaglavlja tabela, standardne rečenice, podnožje i broj strane su na odabranom jeziku.
3. Rječnik ima 630 natpisa i 19 obrazaca.

## Šta ostaje na jeziku na kojem je uneseno

Sačuvani podaci: ocjene, dokazi, nalazi, plan 90 dana i tekst konsultanta. To važi i za METALPRO DEMO simulaciju, čiji su ogledni nalazi i plan uneseni na bosanskom.

## Šta je još na bosanskom

- Izvještaj projekta (PDF i Word) sa ekrana „Projekti”.
- Detalji grešaka koje šalje server (dio poruke iza dvotačke).
- Pojedini sastavljeni tekstovi na ekranima „Projekti” i „Vođeno prikupljanje”, te tekst koji AI servis vrati (promptovi su na bosanskom).

## Pregled prevoda

Prevod kataloga je radni. Stručne izraze (npr. „Scrap and rework”, „Deviation management”, „Site visit”) treba da pregleda vlasnik metodologije prije upotrebe kod klijenta. Ispravke se unose u `mevan_criteria_en.py` i `mevan_i18n.py`, bez izmjene stranica.

## Provjere

- `pytest`: 238 prolaza (235 ranijih + 3 nova): katalog pokriva svih 61 kriterija s istom strukturom, šalje se samo na engleskom i primjenjuje prije upotrebe; Word izvozi koriste rječnik.
- Browser prolaz na engleskom: kriteriji na ekranu modula su na engleskom, sačuvana vrijednost polja ostaje netaknuta, bez JavaScript grešaka. Word izvoz modula nema preostalog bosanskog teksta; u ukupnom detaljnom izvozu na bosanskom ostaju samo sačuvani podaci.
- Oba mobilna toka (na bosanskom) i Word QA 12/12 prolaze.

## Granice

Engleski prevod nije pregledao izvorni govornik ni stručnjak za metodologiju. Provjereno u Chromiumu. Render nije testiran.
