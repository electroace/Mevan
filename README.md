# MEVAN Diagnostic – privatni razvojni demo v1.0

**Nije produkcijska aplikacija.** Ovo je prvi integrisani serverski prototip sa jednom administratorskom prijavom, SQLite pohranom i postojećim METALPRO demo interfejsom.

## Lokalno pokretanje

1. `python -m venv .venv` i aktiviraj virtualno okruženje.
2. `pip install -r requirements.txt`
3. Postavi varijable `MEVAN_ADMIN_EMAIL`, `MEVAN_ADMIN_PASSWORD` (NOVA jaka lozinka, ne ona iz razgovora), `MEVAN_SESSION_SECRET` (32+ nasumična znaka), `MEVAN_SECURE_COOKIE=0` samo za lokalni HTTP.
4. `uvicorn server:app --host 127.0.0.1 --port 8000`
5. Otvori `http://127.0.0.1:8000`.

Za javni hosting obavezno HTTPS, `MEVAN_SECURE_COOKIE=1`, zaseban privatni hosting, enkriptovani backup, zaštita od brute-force pokušaja, CSRF zaštita, revizija pristupa i sigurnosno testiranje. Ovaj prototip **ne treba javno izlagati** dok se navedeno ne implementira. SQLite fajl mora biti na trajnom volumenu; na efemernom hostingu podaci se gube.

## Implementirano
- Serverska prijava jednog administratora putem varijabli okruženja; lozinka nije u HTML-u.
- HTTP-only sesijski kolačić sa potpisom i rokom 8 sati.
- Učitavanje i čuvanje radnog prostora u SQLite bazi.
- Postojeći 61 kriterij, pet modula, METALPRO simulacija, finansijski registar, lokalna pravila analize i Word izvoz.

## Nije završeno
- Stvarni AI servis, višekorisničke uloge, audit log, dokumentni storage, automatizovani Word QA, sigurnosno očvršćavanje, hosting i produkcijska validacija.
- Analitički nacrti su i dalje **zasnovani na pravilima**, nisu generativni AI.

## Novo u v1.1 – AI nacrt
- Opcionalni endpoint `/api/ai/draft`, koristi serverski `OPENAI_API_KEY` (nikada ne stavljati ključ u HTML).
- Model se može promijeniti varijablom `MEVAN_AI_MODEL`. API pozivi mogu imati trošak.
- AI vidi poslane nalaze, ocjene i tekst dokaza. **Ne unositi stvarne povjerljive podatke bez odgovarajuće pravne i sigurnosne procjene.**
- Ako ključ nije postavljen, radi samo postojeća analiza po pravilima.
- Nacrt ne znači odobrenje. Sadržaj mora provjeriti konsultant.
- Osnovno ograničenje pokušaja prijave i provjera Origin zaglavlja dodani su, ali **ovo nije kompletno sigurnosno očvršćavanje**.
- Prije javne objave obavezni su CSRF tokeni, perzistentno ograničavanje prijava, audit log, upravljanje tajnama, backup i testiranje.

## v1.2 – provjere integracije i kontrola izvora
- Dodani automatizovani offline testovi: zaštita pristupa, prijava, SQLite upis/čitanje, validacija zahtjeva, AI bez ključa, odjava.
- Mutirajući zahtjevi zahtijevaju odgovarajući `Origin` ili `Referer`; za hosting postaviti `MEVAN_PUBLIC_ORIGIN=https://...`.
- **Nije spremno za javno postavljanje.** Nisu završeni sigurnosna revizija, trajno ograničavanje pokušaja, backup/restore, revizijski dnevnik, upravljanje pristupom i test stvarnog AI servisa.
- Pokrenuti testove: `python -m unittest -v test_integration.py`.

## v1.3 – sigurnosna kopija i revizijski trag
- Administratorski JSON izvoz putem `/api/backup` i dugmeta u aplikaciji.
- Vraćanje JSON kopije uz dvostruku potvrdu; **prepisuje trenutne podatke**.
- Revizijski dnevnik: prijava, odjava, spremanje, izvoz i vraćanje podataka; zadnjih 100 zapisa `/api/audit`.
- Kopije se preuzimaju lokalno i **nisu automatski šifrovane**. Čuvati ih na sigurnom mjestu.
- Ovaj demo i dalje nije spreman za javno izlaganje: nema produkcijski backup raspored, vanjski audit, TLS konfiguraciju, kontrolu konkurentnog uređivanja ni pun sigurnosni pregled.


## v1.4 – kontrola izvještaja
- Kontrola odobrenja sada uključuje i sadržaj odobrenog teksta: naknadna izmjena automatski poništava važenje odobrenja u Word izvještaju.
- `qa_word_reports.js` generiše svih 12 DOCX izvještaja iz METALPRO DEMO simulacije.
- `qa_word_reports.py` provjerava strukturu, XML i sadržaj svih 12 dokumenata.
- Ovi testovi ne zamjenjuju vizuelni pregled niti provjeru stvarnog AI servisa.

## v1.5 – paket za privremeni hosting
Dodani Dockerfile, Compose, konfiguracija, sigurnosna zaglavlja i upute u `DEPLOY_PRIVREMENA_ADRESA.md`. Paket **nije hostovan** i ne predstavlja potvrdu produkcijske sigurnosti.
