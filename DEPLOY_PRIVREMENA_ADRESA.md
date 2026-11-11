# MEVAN – priprema privremene web-adrese (v1.5)

**Status: paket za postavljanje, NIJE objavljeno na internetu.**

## Preduvjeti
- VPS s Docker Compose, HTTPS reverse proxy (Caddy/Nginx), privatna privremena domena/subdomena i pristup DNS-u.
- Prije hostinga obavezna sigurnosna revizija: ova aplikacija još nije produkcijski očvrsnuta.
- Ne koristiti lozinku prethodno poslanu u razgovoru. Postaviti novu, jedinstvenu i jaku lozinku.

## Koraci za administratora hostinga
1. Kopirati `.env.example` u `.env` i unijeti **novu** lozinku, nasumični session secret, tačnu HTTPS adresu i dozvoljeni host.
2. Postaviti `.env` dozvole na 600. Ne dijeliti ni commitovati `.env`.
3. Pokrenuti `docker compose up -d --build` (port 8000 dostupan samo lokalnom serveru).
4. Konfigurisati HTTPS reverse proxy na `127.0.0.1:8000`; dozvoliti pristup samo ovlaštenom korisniku, idealno dodatni VPN ili IP allowlist.
5. Testirati prijavu, odjavu, unos METALPRO podataka, Word izvoz, AI bez ključa, backup i restore.
6. Uspostaviti **automatski šifrovan** dnevni backup trajnog Docker volumena, offsite kopiju i test vraćanja.
7. Prije stvarnih podataka provjeriti zaštitu ličnih podataka i ugovor s hostingom/AI pružaocem.

## Sigurnosne granice
- Osnovno ograničenje pokušaja prijave čuva se u RAM-u; restart ga briše.
- Nema potpunog CSRF token mehanizma, upravljanja aktivnim sesijama, 2FA, niti produkcijske revizije.
- AI zahtijeva zaseban API ključ i troškove; trenutno nije aktiviran.
- Jedna SQLite baza za jednu administratorsku instancu; ne pokretati više replika.
- `MEVAN_ENABLE_HSTS=1` koristiti samo iza pravilno konfigurisanog HTTPS-a.
- Ne povezivati mevan.ba prije pregleda i korisničkog odobrenja.

## Korak 22: backup / restore (administrator)
Prije rada sa stvarnim podacima podesiti dnevni raspored, šifrovanje i offsite čuvanje.
Za ručnu probu na **kopiji testne baze**:

```bash
python backup_restore.py backup /data/mevan.sqlite3 /sigurna-lokacija/mevan-test-backup.db
python backup_restore.py verify /sigurna-lokacija/mevan-test-backup.db
python backup_restore.py restore /sigurna-lokacija/mevan-test-backup.db /sigurna-lokacija/mevan-test-restore.db
```

`restore` nikad ne prepisuje postojeću bazu. Ne mijenjati putanju aktivne baze dok aplikacija radi. Ovaj primjer nije automatizirani niti šifrovani backup.
