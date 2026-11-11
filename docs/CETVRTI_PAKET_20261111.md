# Četvrti paket — 11.11.2026. (korak 1: meni i zaglavlje)

Osnova: treći paket. Mijenja se samo raspored, nazivi i izgled navigacije. Poslovna logika, API, baza i izvještaji nisu mijenjani.

## Šta je promijenjeno

1. **Isti meni i zaglavlje na sva četiri ekrana** (Dijagnostika, Vođeno prikupljanje, Projekti, Pregled portfolija). Meni je u novom modulu `mevan_nav.py`; server ga ubacuje u postojeće HTML stranice preko tri oznake mjesta.
2. **Meni je grupisan po toku rada:** Kompanija, Procjena, Analiza i izvještaji, Projekti; na dnu „Podaci i sigurnost” i „Odjava”.
3. **Nazivi na bosanskom, bez tehničkih oznaka:** „Projekti” (ranije „MEVAN 4.0 · Projekti TEST”), „Pregled portfolija” (ranije „Portfolio dashboard”), „Finansijski efekti”, „Pregled”, „Integrisana analiza (AI)”, „Vođeno prikupljanje”.
4. **Telefon:** meni se otvara dugmetom „Meni” i zatvara se nakon izbora, tipkom Escape ili dodirom pored menija.
5. **Adresa pamti stranicu:** npr. `/#report`. Osvježavanje ostaje na istoj stranici, a meni s drugih ekrana vodi direktno na izabranu stranicu.
6. **Sigurnosna kopija na serveru** premještena je iz lebdećeg okvira u uglu na stranicu „Podaci i sigurnost”. Potvrde pri vraćanju su iste.

## Šta nije mijenjano

Nijedna funkcija nije uklonjena. Sve ranije stavke menija postoje pod istim `data-page` oznakama. Dugmad unutar stranica još nisu standardizovana; to je korak 2.

## Provjere

- `pytest`: 180 prolaza (172 ranija + 8 novih u `tests/test_package4_nav.py`).
- Word QA 12/12.
- Oba postojeća mobilna browser toka prolaze; u njih je dodat samo korak otvaranja menija na telefonu.
- Ručni browser prolaz na 1366 px i 390 px: svi ekrani, direktni linkovi, osvježavanje, zatvaranje menija, bez JavaScript grešaka.

## Granice

Provjereno u Chromiumu. Safari i Firefox nisu testirani. Stvarni AI, Render i udaljeni PostgreSQL nisu testirani.
