# Prvi paket — efekti, konsultantski pregled i Word QA

Osnova: `mevan-v2-test`, `85fd230eb7d781bb6d25b3e8f1552f8e54f31a2b`.
Opseg: isključivo tri korisnički odobrene popravke. Nema deploya, promjene
Render postavki, produkcijske migracije ili čišćenja postojećih podataka.
N/P pravila, DEMO status i težine C1/C2/C3 ostaju isti.

## Finansijski efekti

Ponovljeni isti zahtjev za isti projekat vraća isti zapis, bez novog efekta
ili audit događaja. Stabilni UUID i `BEGIN IMMEDIATE` koriste postojeću šemu.
Iznosi `4000` i `4000.00` imaju isti identitet zahtjeva. Odgovor zadržava HTTP
201 uz `replayed=true` kada je zahtjev već evidentiran.

Opcionalni `Idempotency-Key`, u obrascu „Oznaka zasebnog događaja”, omogućava
različite stvarne događaje s jednakim vrijednostima. Oznaka važi unutar projekta;
ista oznaka s drugim sadržajem vraća 409. Bez oznake koristi se normalizirani
sadržaj. Za ponavljanje zahtjeva potrebno je zadržati istu oznaku i sadržaj.

Raniji nasumični UUID zapisi i duplikati ostaju netaknuti; zaštita novih upisa
ne može rekonstruisati identitet ranijih mrežnih zahtjeva. Sistem ne potvrđuje
poslovnu istinitost korisničke tvrdnje da dva događaja zaista jesu različita.

## Novo konsultantsko odobrenje

Tehnička provjera odbija prazne, zamjenske i besmisleno kratke unose:

| Polje | Najmanje znakova | Najmanje riječi |
|---|---:|---:|
| Sažetak | 80 | 12 |
| Svaki prioritet | 40 | 6 |
| Svaki period plana | 60 | 10 |

Najviše je 6000 znakova po polju; provjeravaju se ponavljanja i poznate
zamjenske oznake. Pravilo važi za novo API odobrenje. Radni nacrti i čitanje
historijskih odobrenih snimaka nisu retroaktivno uslovljeni novim pragovima.
Ovo nije stručna ocjena kvaliteta, istinitosti dokaza ili poslovne vrijednosti.

## Word testni paket

Stari marker `cloudBoot();` neposredno ispred završnog script taga više nije
postojao; izdvajanje je zato uključivalo naredni HTML i izazivalo sintaksnu
grešku. Harness sada izdvaja tačno jedan stvarni glavni script blok i kompajlira
ga u cjelini, uključujući kod poslije `cloudBoot()`.

Zastarjela provjera riječi „NEODOBRENI” usklađena je s postojećom oznakom
„Status analize: Neodobreno / promijenjeni podaci.”. ZIP/XML provjere ostaju;
dodane su provjere svih 12 naziva, oznaka simulacije i zabrana odobrenog statusa.
Namjerno pokvaren status mora oboriti validator. Postojeći DOCX rezultati se
ne prepisuju; novi direktorij bira se varijablom `MEVAN_WORD_QA_DIR`.

## Lokalna provjera na izolovanim podacima, 10.11.2026.

- Cijeli paket: **136 prolaza**, jedno Starlette/httpx upozorenje, 15,57 s.
- Ciljani paket: **31 prolaz**, dio istog opsega provjera, ne dodatno na 136.
- Word: **12/12** ZIP/XML/sadržajnih provjera.
- Šest istovremenih ponavljanja, sa i bez oznake: jedan efekat i jedan audit.
- Dvaput poslano 4.000 KM ostaje jedan efekat od 4.000 KM.
- „x” u sedam polja odbijen; valjan bosanski pregled prihvaćen.
- Historijski kratak odobreni sadržaj ostaje čitljiv u četiri izvoza.
- Mobilni Chromium tok na 390×844 prošao je, uključujući četiri pročitana
  PDF/DOCX izvoza, ponovljeni efekat i odvojeni događaj; C1/C3/C2 ostaje 81/72/67.

AI odgovor u browser testu je zadat, a dokazi su sintetički. **Stvarni AI i
Render nisu testirani.** PDF prva stranica je vizuelno pregledana; ne tvrdi se
vizuelna provjera DOCX rasporeda u Wordu/LibreOfficeu. Raniji izvještaji,
registri i testni rezultati ostaju sačuvani izvan commita; generisane baze,
dokumenti, slike, logovi i stvarni pristupni podaci nisu dio ovog paketa.
