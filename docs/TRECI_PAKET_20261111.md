# Treći paket — 11.11.2026.

Osnova: lokalni paket 2, commit `132ef288917b0573709655437cb8904574898015`. Paket je pripremljen kao patch; nema pusha, PR-a ni deploya iz same pripreme.

## Šta je promijenjeno

1. **Neispravan finansijski model vraća 422 umjesto 500.** `POST /api/v4/financial-scenarios/calculate` i `PUT /api/v4/projects/{pid}/financial-model` sada hvataju grešku validacije i vraćaju poruku na bosanskom. Ništa se ne upisuje u bazu ni u audit kada je unos neispravan. Ispravni unosi rade kao prije.
2. **Ocjena 0 ostaje vidljiva u AI kontekstu.** U `/api/v3/analyze` numerička ocjena 0 se više ne pretvara u prazno polje. Prazna i nepostojeća ocjena i dalje ostaju prazne. Deterministički obračun indeksa nije mijenjan.
3. **Zaključane verzije za hosting.** Novi `requirements.lock` sadrži tačne verzije s kojima su prošli svi testovi. `Dockerfile` instalira iz tog fajla. `requirements.txt` i CI nisu mijenjani.

## Šta nije mijenjano

Težine C1/C2/C3, N/P pravila, DEMO režim, vođeni tok, izvještaji, šema baze i Render postavke.

## Provjere

- `pytest`: 172 prolaza (168 ranijih + 4 nova u `tests/test_package3_fixes.py`), jedno poznato upozorenje.
- Word QA: 12/12.
- `http_release_smoke.py`: prolazi.
- Isto ponovljeno u čistom okruženju instaliranom samo iz `requirements.lock`.

## Granice

Docker image nije izgrađen u ovoj provjeri; zaključane verzije su provjerene u čistom Python 3.12 okruženju. Browser testovi, stvarni AI, Render i udaljeni PostgreSQL nisu testirani.
