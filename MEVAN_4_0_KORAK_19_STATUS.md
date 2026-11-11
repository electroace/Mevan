# MEVAN 4.0 — Korak 19: release QA

- Ispravljena validacija ISO sedmica sedmičnih pregleda. Format YYYY-Www nije dovoljan: sedmica mora stvarno postojati u navedenoj ISO godini.
- Dodana dva regresijska testa: ispravnost sedmica i odbijanje neispravnih API unosa bez promjene baze ili historije.
- Lokalno: 49/49 pytest testova prolazi, Python sintaksa provjerena.
- Chromium pokušaj i dalje blokiran pravilom okruženja (ERR_BLOCKED_BY_ADMINISTRATOR); ne predstavlja uspješan browser test.
- Live OpenAI nije testiran. Nije bilo GitHub/Render deploya ni izmjene produkcijskog main.
- Paket je razvojni TEST, nije produkcijski release.
