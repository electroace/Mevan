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

## Dopuna 9.1 — Claude vraća HTTP 400 na „Provjeri vezu”

**Greška:** uz servis Claude (Anthropic) provjera veze i svi AI pozivi vraćali su HTTP 400. Uzrok: aplikacija je slala parametar `temperature`, a noviji Claude modeli odbijaju svaku vrijednost osim zadane.

**Popravka:**
- Za Claude se `temperature` više ne šalje. Za OpenAI i kompatibilne servise zahtjev je isti kao prije.
- Noviji Claude modeli razmišljaju prije odgovora i to troše iz `max_tokens`, pa Claude zahtjev dobija rezervu od 4096 tokena da odgovor ne bude odsječen. Odgovor se i dalje čita po vrsti bloka, pa blok razmišljanja ispred teksta ne smeta.
- „Provjeri vezu” sada uz HTTP kod prikazuje i kratko objašnjenje samog servisa (npr. nedovoljno kredita ili nepodržan parametar). Ključ se iz te poruke uklanja.

**Posljedica:** bez niske temperature Claude odgovori mogu biti nešto manje ujednačeni između dva pokretanja nego ranije zamišljeno. Stručni pregled nacrta ostaje obavezan kao i dosad.

**Provjere:** `pytest` 240 prolaza (dva nova testa i dopunjen test oblika Claude zahtjeva). Stvarni poziv Anthropic servisu i dalje nije izvršen iz razvojnog okruženja.

## Dopuna 9.2 — „AI nije vratio ispravan strukturirani nacrt” uz Claude

**Problem:** integrisana analiza je uz Claude servis vraćala opću poruku „AI nije vratio ispravan strukturirani nacrt; ništa nije odobreno.” bez razloga. Stroga provjera nacrta je ispravna i ostaje; nedostajali su razlog i dovoljno prostora i vremena za Claude odgovor.

**Popravka:**
- Poruka sada navodi razlog: prekinut odgovor, neispravan JSON, polje koje nedostaje ili provjera koja nije prošla (npr. „Nepotpuna KPI definicija”). Razlog se bilježi i u dnevnik kao `v3_ai_draft_rejected`.
- Istek vremena ima svoju poruku („AI servis nije odgovorio na vrijeme”).
- Za Claude: dvostruko veći prostor za odgovor uz rezervu za razmišljanje, čekanje do 240 sekundi i veći dozvoljeni odgovor servisa.
- Ako servis vrati tekst oko JSON objekta, objekat se izdvaja. Ako je odgovor odsječen zbog dužine, to se prijavljuje kao razlog umjesto pokušaja čitanja nepotpunog JSON-a (za sve servise).

**Provjere:** `pytest` 242 prolaza (dva nova testa). Mobilni tok s integrisanom analizom prolazi. Stvarni poziv Anthropic servisu nije izvršen iz razvojnog okruženja.

## Dopuna 9.3 — „Unexpected token '<' … is not valid JSON” pri integrisanoj analizi

**Greška:** preglednik je umjesto odgovora aplikacije dobio HTML stranicu greške s hostinga. Dva uzroka u aplikaciji:
- AI poziv se izvršavao u glavnoj petlji servera, pa server za to vrijeme nije odgovarao ni na šta, ni na provjeru zdravlja (`/health`) kojom hosting utvrđuje da je servis živ.
- Cijela analiza je bila jedan dug HTTP zahtjev; uz Claude može trajati duže nego što mreža ispred servera drži zahtjev otvorenim.

**Popravka:**
- Svi AI pozivi se izvršavaju u zasebnoj niti; server ostaje dostupan dok AI radi.
- Integrisana analiza je pozadinski posao: `POST /api/v3/analyze/start` vraća oznaku posla, a preglednik svake tri sekunde pita `GET /api/v3/analyze/job/{oznaka}` dok rezultat ne stigne (najduže oko sedam minuta). Stari `POST /api/v3/analyze` i dalje radi.
- Ako server ipak vrati nešto što nije JSON, korisnik vidi razumljivu poruku umjesto tehničke greške.

**Ograničenja:** poslovi se drže u memoriji jednog procesa. Ako se server ponovo pokrene dok analiza traje, posao nestaje i analizu treba pokrenuti ponovo (aplikacija to kaže). Nacrt po modulu („AI nacrt (server)”) i dalje je jedan zahtjev, ali više ne blokira server.

**Provjere:** `pytest` 245 prolaza (tri nova testa: posao u pozadini dok `/health` odgovara, zaštita novih adresa, AI pozivi izvan glavne petlje). Mobilni browser tok prolazi kroz novi način pokretanja i čitanja analize. Stvarni poziv Anthropic servisu i Render nisu testirani iz razvojnog okruženja.

## Dopuna 9.4 — rezultat integrisane analize se čuva

**Problem:** rezultat integrisane analize postojao je samo u memoriji otvorene stranice. Odlazak na drugi ekran, osvježavanje ili zatvaranje prozora brisali su ga.

**Rješenje:**
- Završena analiza se upisuje u dijagnostiku (`v3`: rezultat, potpis ulaznih podataka, vrijeme). Zato ide u lokalnu kopiju u pregledniku, sinhronizuje se na server kao i ostali podaci, i dio je JSON sigurnosne kopije.
- Svaka dijagnostika ima svoju analizu; nova analiza zamjenjuje prethodnu za tu dijagnostiku.
- Ispod dugmadi piše kada je analiza sačuvana. Ako su ocjene ili finansijski efekti od tada mijenjani, piše da analiza više nije ažurna (rezultat ostaje vidljiv).
- Ako se stranica napusti dok analiza još traje, oznaka posla ostaje zapamćena u pregledniku. Pri povratku na „Integrisana analiza (AI)” rezultat se preuzima i čuva. Server drži rezultat 30 minuta.
- Nedovršena analiza ne briše prethodno sačuvanu: ako novo pokretanje ne uspije, prikazuje se greška i ranija analiza.

**Ograničenja:** analiza pokrenuta u jednom pregledniku preuzima se samo iz tog preglednika. Ako se server ponovo pokrene dok analiza traje, posao se gubi i treba je pokrenuti ponovo. Ako hosting nema trajni disk, serverska kopija se gubi s novim deployem kao i ostali podaci; lokalna kopija u pregledniku ostaje.

**Provjere:** `pytest` 247 prolaza (dva nova testa). Browser prolaz: pokretanje analize pa odlazak na drugi ekran i povratak, puno osvježavanje, drugi preglednik (rezultat stiže sa servera), izmjena ocjene (oznaka neažurnosti), nova dijagnostika bez tuđe analize; bez JavaScript grešaka. Oba mobilna toka i Word QA 12/12 prolaze.
