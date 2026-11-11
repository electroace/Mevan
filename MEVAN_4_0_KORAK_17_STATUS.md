# MEVAN 4.0 — korak 17 (testni paket)

- Dodana trajna SQLite historija kreiranja projekata, izmjena Chartera i prelazaka u validaciju/implementaciju.
- Novo autentificirano čitanje historije: `GET /api/v4/projects/{pid}/audit`.
- Svaka izmjena čuva prethodni i novi sadržaj; identični upis ne dodaje događaj.
- Dodan regresijski test historije i pristupa.
- Pokušaj Playwright/Chromium browser testa i dalje blokira politika izvršnog okruženja (`net::ERR_BLOCKED_BY_ADMINISTRATOR`); ne smije se označiti kao uspješan browser test.
- Nema izmjena na GitHubu, Renderu ni produkcijskom `main`.
- Audit trenutno pokriva Charter i odobrenja, ne sve finansijske/sedmične promjene; nije zamjena za potpun sistem verzionisanja i kontrole ovlaštenja.
