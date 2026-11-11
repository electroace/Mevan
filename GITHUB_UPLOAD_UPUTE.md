# MEVAN 4.0 — Sigurna testna implementacija

**Ne mijenjati `main`. Ne postavljati stvarne podatke klijenata.**

1. Napraviti sigurnosnu kopiju postojeće testne grane `mevan-v2-test` i potvrditi da je odabrana upravo ta grana.
2. Raspakovati ovaj ZIP i dodati izmijenjene aplikacijske fajlove na `mevan-v2-test` (bez `.env`, baza podataka, ZIP-ova i testnih izlaznih dokumenata).
3. Prije pokretanja provjeriti `python release_preflight.py`; nakon postavljanja sigurnih tajni i stvarne HTTPS testne domene pokrenuti `python release_preflight.py --runtime`.
4. Docker Compose varijanta koristi lokalni port `127.0.0.1:8000`, zaseban volume `mevan_data` i HTTPS reverse proxy. **Render ne koristi automatski `compose.yaml`**: potrebna je odvojena konfiguracija servisa, perzistentnog diska, tajni i hosta.
5. Testirati Docker build/start, `/health`, prijavu/odjavu, projektni ekran, dashboard, METALPRO DEMO, Word/PDF izvoz i backup/restore. Tek nakon toga konsultantska provjera u pregledniku.
6. Produkcijski `main` i produkcijsku bazu ne dirati.

**Status:** offline QA završen, testna implementacija još nije izvršena.
