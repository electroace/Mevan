> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: stvarni admin ulazi, prava, funkcije i eksplicitno odsutne oblasti.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — administratorski pristup i mogućnosti

## Stvarni administratorski model

Ne postoji zaseban `/admin` panel niti users/roles tabela. `server.py:14` čita jedan e-mail, jednu lozinku i session secret iz env-a; `server.py:101` login formom daje jedinstvenu sesiju. Svi zaštićeni ekrani predstavljaju isti administrator/konsultant pristup. Na dashboardu fraza „projekti prijavljenog konsultanta” ne znači per-user ownership: svi projekti ove instance su dostupni istom loginu. Prava nisu odvojena za vlasnika, konsultanta, finansije i klijenta. Postojeći rad ne smije se ukloniti pri kasnijem uvođenju uloga.

## Matrica administracije

| Oblast | Stvarno dostupno | Pristup / izvori | Šta nedostaje / rizik |
|---|---|---|---|
| Prijava/odjava | Jedan env admin, potpisana sesija, login CSRF/IP limit | /login,/logout; `server.py:71`/`:101` | Nema reset lozinke/MFA/revokacije sesije po ID-u |
| Korisnici/uloge | Nije implementirano | Nema users tabele ili CRUD ruta | Ne prikazivati kao skriven admin panel |
| Kompanije/dijagnostike | Kreiranje/odabir/preimenovanje kroz glavni workspace; profil | `/` workspace; `/api/workspace` | JSON organizacija, bez tenant ACL/RLS; whole workspace upis |
| Paketi/pretplate/cijene/PDV | Nije implementirano | Nema modela/ruta/tabela | Tehnički limiti nisu planovi naplate |
| Aktivnosti/projekti | Charter, validacija/implementacija, sedmični pregledi | `/projects-ui`, `/api/v4/projects...` | Nema aktivnog close/delete endpointa, iako status closed postoji |
| Simulacije | Vrati METALPRO, eksplicitni DEMO pregled/seed, zaključavanje simuliranog snimka | `/`, `/diagnostic-review` | Nema stvarne verifikacije; DEMO ne dobija implementaciju |
| Dokumenti | Radni i zaključani PDF/DOCX + projektni izvještaji | Glavni/Guided/projektni ekran | Nema centralnog upload/archive managera ni numeracije računa |
| Ograničenja | Body/list/text granice u validatorima | `server.py:147`, `mevan_sync_guard.py:19`, Pydantic modeli | Nema admin UI za promjenu limita/paketa/težina |
| Finansije | Scenarijske procjene i konsultantski evidentirani efekti | Projektni UI/API | Nije računovodstvo ili naplata; nezavisna verifikacija nije dostupna kroz actual form |
| Audit | /api/audit zadnjih 100 + project/{id}/audit | Sesija; read-only API | Nema WORM, vanjske arhive, per-user identiteta ili full audit ekrana |
| Backup/restore | browser JSON; legacy serverski JSON; offline SQLite CLI; TEST helper | `/api/backup`, `/api/backup/restore`, `backup_restore.py:24` | Nema rasporeda/šifrovanja/offsite/punog multi-store restore dugmeta |
| Hosting/tajne | Operator izvan aplikacije | Env/Render dashboard odvojeno | Nema aplikacijskog deploy, env ili billing administratora |

## Tipične administratorske procedure

Dodavanje kompanije ne kreira novi račun ili izolovanu bazu. U radnom prostoru izabrati kompaniju/dijagnostiku, popuniti profil i kriterije; spremanje ide cijelim JSON workspaceom uz If-Match. N/P mora imati razlog i imenovanu potvrdu. Za finalni izvještaj ući u Guided, pregledati izvore, rizike, sažetak/prioritete/plan, odabrati real ili demo i zaključati samo valjanu reviziju. Stara odobrenja ostaju dostupna u listi.

Projekt: učitati analizu/kandidate, procijeniti pet faktora, izabrati draft, potvrditi osnovicu/ciljeve/checks tek nakon stvarnog rada. Samo flagovi u formi ne znače nezavisan audit. DEMO projekat ostaje neimplementabilan. Zaseban legitimni finansijski događaj može imati novu oznaku; mrežni retry treba isti event key. Nema masovnog čišćenja starih efekata.

Backup postupak mora prvo odrediti obuhvat. UI JSON nije arhiva svih tabela. Legacy restore prepisuje legacy workspace uz header potvrdu, ne vraća audit/projekte. Offline SQLite restore ide na novu putanju uz zaustavljenu aplikaciju prije prebacivanja DB varijable. Vanjski PostgreSQL i prilozi zahtijevaju zaseban postupak koji nije implementiran ovim panelom. Detalji u [arhitekturi](DATABASE_AND_ARCHITECTURE.md) i [infrastrukturi](INFRASTRUCTURE_AND_DEPLOYMENT.md).

## Greške i nedozvoljene pretpostavke

401 znači nema valjane sesije, 403 porijeklo/token, 409 konflikt/status/isti event s drugim sadržajem, 422 validacija/gate. Server-side odluka ima prednost nad vidljivim dugmetom. Admin ne može kroz UI uključiti AI ključ ili Render auto-deploy. Promjena env lozinke ne revocira postojeće sesije ako secret/e-mail identitet ostaje isti. Nema pojedinačnih dozvola nad kompanijom; zato ovaj model nije spreman za više nepovezanih klijenata u jednoj instanci.

Novi zadatak dokumentacije nije odobrenje stvarnog restorea, promjene admin kredencijala ili postavki hostinga. U ovom paketu nema stvarnih identiteta/lozinki/API ključeva/deploy hooka. Sve procedure su upute za naknadno autorizovanog operatora.

Povezano: [funkcionalni API](FUNCTIONAL_SPECIFICATION.md), [potpuni UX inventar](UI_UX_SPECIFICATION.md), [sigurnost](SECURITY.md), [glavni status](MASTER_PROJECT.md).
## Poslovne funkcije koje ne postoje

Ovo nije fakturisanje ili generički SaaS. Nema registracije, verifikacije e-maila, resetovanja lozinke, pozivnica, korisničke tabele, paketa besplatno/plaćeno, pretplata, kartičnog plaćanja, billing portala, cijena/licenci, PDV obračuna, računa/predračuna, kupaca, artikala ili cjenovnika. Pominjanje kupca/proizvoda u pitanju F02 nije CRM/skladišna funkcija. KM je jedinica finansijskih procjena i evidentiranih efekata, nije cijena softvera. Nema automatizovanih e-mailova, Cloudflare/Supabase autentifikacije ili RLS-a. Odgovarajući testovi tih nepostojećih tokova su N/A, a ne „passed”. Nema pretpostavljene zakonske formule PDV ili numeracije računa.
