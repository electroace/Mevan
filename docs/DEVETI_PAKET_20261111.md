# Deveti paket — 11.11.2026. (izbor AI servisa i vlastiti API ključ)

Osnova: osmi paket. Promptovi, obračuni, izvještaji i tok odobravanja nisu mijenjani; mijenja se samo kome se AI zahtjev šalje i odakle dolazi ključ.

## Šta je novo

1. **Stranica „Podaci i sigurnost” ima dio „AI servis”:** izbor servisa, naziv modela, API ključ, dugmad „Sačuvaj AI postavke”, „Provjeri vezu” i „Ukloni ključ”.
2. **Tri vrste servisa:** ChatGPT (OpenAI), Claude (Anthropic) i drugi servis s OpenAI-kompatibilnim API-jem (uz https adresu servisa).
3. **Svih pet AI funkcija koristi odabrani servis:** nacrt po modulu, integrisana analiza (v2.2, v2.3, v3) i AI projektni nacrt. Pozivi idu kroz jedan modul, `mevan_ai.py`.
4. **Varijable okruženja i dalje rade.** Ako ključ nije unesen u aplikaciji, koristi se `OPENAI_API_KEY` i `MEVAN_AI_MODEL` kao dosad. Ključ unesen u aplikaciji ima prednost.

## Kako se ključ čuva

- Šifrovan u bazi (Fernet iz paketa `cryptography`; ključ šifre izveden je iz `MEVAN_SESSION_SECRET`).
- Server ga nikad ne vraća pregledniku; vide se samo zadnja četiri znaka.
- Nije u JSON sigurnosnim kopijama ni u revizijskom dnevniku (dnevnik bilježi samo servis i model).
- Poruke o grešci sadrže samo HTTP kod servisa, ne njegov odgovor.
- Adresa „drugog servisa” mora biti javna https adresa (lokalne i privatne adrese se odbijaju).

## Ograničenja koja treba znati

- Šifrovanje štiti ako procuri datoteka baze ili kopija. Ne štiti ako je kompromitovan sam server, jer je tajna na istom serveru.
- Ako se promijeni `MEVAN_SESSION_SECRET`, sačuvani ključ se više ne može pročitati i treba ga unijeti ponovo.
- Ako je SQLite baza na disku koji se briše pri novom deployu (npr. Render bez trajnog diska), ključ se gubi sa svakim deployem, kao i ostali podaci.
- Claude nema `response_format`; za JSON odgovore se šalje dodatna uputa i uklanjaju se oznake koda oko odgovora.
- Noviji OpenAI modeli s drugačijim parametrima (npr. bez `max_tokens`) nisu podržani; oblik zahtjeva je isti kao i dosad.

## Zavisnosti

Dodan je paket `cryptography` (`requirements.txt` i `requirements.lock`, s `cffi` i `pycparser`). Hosting ga instalira pri sljedećoj izgradnji.

## Provjere

- `pytest`: 224 prolaza (208 ranijih + 16 novih u `tests/test_package9_ai_settings.py`): ključ se ne vraća i nije čitljiv u bazi, kopiji ni dnevniku; prijava i izvor su obavezni; prazan ključ zadržava postojeći samo za isti servis; neispravan unos se odbija; okruženje i dalje radi; promijenjena tajna; oblik zahtjeva za sva tri servisa; provjera veze; AI nacrt ide odabranom servisu.
- Browser prolaz na 1366 px i 390 px s izmišljenim ključem: čuvanje, status, provjera veze (odbijena, s jasnom porukom), uklanjanje; ključ se ne pojavljuje u stranici nakon čuvanja.
- Oba mobilna toka i Word QA 12/12 prolaze.

## Šta nije testirano

Nijedan stvarni poziv OpenAI, Anthropic ili trećem servisu nije izvršen, jer za to treba stvarni ključ. Provjeren je samo oblik zahtjeva i obrada odgovora. Prvi stvarni test je dugme „Provjeri vezu” nakon unosa ključa.
