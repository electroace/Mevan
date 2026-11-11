# MEVAN 4.0 — Korak 21: Izolovani HTTP release smoke test

- Dodan `http_release_smoke.py` za pokretanje stvarnog lokalnog Uvicorn servera s privremenom SQLite bazom i isključivo testnim podacima.
- Provjerava zabranu anonimnog pristupa, CSRF prijavu, sesiju, tri HTML ekrana i workspace API.
- Ne šalje podatke OpenAI servisu i ne pristupa produkciji.
- Browser/Chromium i dalje blokira lokalne URL-ove administrativnim pravilom; HTTP test ne zamjenjuje browser test.
- GitHub/Render deploy nije izvršen.
