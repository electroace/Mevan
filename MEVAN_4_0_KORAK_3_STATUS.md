# MEVAN 4.0 — razvojni korak 3 (lokalni test)

Dodano: `project_planner.py` s determinističkim rangiranjem prema profitu (25%), likvidnosti (20%), isporuci (25%), riziku (20%) i izvedivosti (10%). Težine su **privremena konfiguracija za test**, nisu odobrena univerzalna metodologija. Ocjene 0–5 i obrazloženja unosi konsultant; sistem označava faktore bez referenci na dokaze. Nema automatskog pretvaranja procjena u potvrđene rezultate.

Novi zaštićeni endpointi: `POST /api/v4/rank-projects`, `POST /api/v4/project-draft`. Drugi pravi preliminarni strukturirani Charter nacrt, s obaveznom validacijom i praznim finansijskim efektima. Nije implementirana AI generacija cjelovitog plana, korisnički ekran, Word/PDF izvoz ili verifikacija u stvarnoj kompaniji.

Lokalno: `python -m unittest discover -p 'test_*.py' -q` → 12 testova uspješno. Testovi ne zamjenjuju sigurnosni audit, testove baze na Renderu ili korisničko prihvatanje.

**NE POSTAVLJATI NA GITHUB/RENDER** — radni paket, produkcijski main nije mijenjan.
