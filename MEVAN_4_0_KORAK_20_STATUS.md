# MEVAN 4.0 — Korak 20: Docker release preflight

- Otkriven i ispravljen kritičan nedostatak: Dockerfile nije uključivao `project_*.py`, `projects_ui.html` i `dashboard_ui.html`, pa Docker instanca ne bi mogla učitati v4 module.
- Dodan `release_preflight.py`: offline provjera sadržaja Docker paketa i opcionalno (`--runtime`) sigurnosnih konfiguracijskih varijabli. Ne ispisuje vrijednosti tajni.
- Dodana tri regresijska testa za sadržaj paketa i validaciju konfiguracije.
- Lokalno: 52/52 pytest testova prolazi, compileall prolazi, offline preflight prolazi.
- Docker build/run nije provjeren (Docker nije dostupan). Chromium browser i stvarni OpenAI poziv nisu provjereni.
- Nema pristupa za GitHub/Render deploy; produkcijski `main` nije mijenjan.
- Paket je namijenjen isključivo testnoj grani `mevan-v2-test`, uz zasebnu bazu i DEMO podatke.
