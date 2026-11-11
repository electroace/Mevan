# Jedanaesti paket — 11.11.2026. (izbor razmišljanja, upozorenje o kreditima, mjesečni limit AI poziva)

Osnova: paket 9.4. Promptovi, obračuni, izvještaji i tok odobravanja nisu mijenjani.

## Šta je novo

1. **Izbor dubine razmišljanja za Claude** („Podaci i sigurnost” → „AI servis” → „Razmišljanje (samo Claude)”): zadano za model, nisko, srednje, visoko, vrlo visoko. Šalje se kao `output_config.effort`. Niže razmišljanje je brže i troši manje; više je sporije i skuplje. Za druge servise se ne šalje.
2. **Upozorenje prije svakog AI poziva.** Integrisana analiza, AI nacrt po modulu i AI projektni nacrt prvo prikažu prozor: koji servis i model se koriste, koja dubina razmišljanja, da se troše krediti na računu servisa i koliko je AI poziva ovog mjeseca već napravljeno. Poziv kreće tek nakon „Pokreni i potroši kredite”.
3. **Mjesečni limit AI poziva** (0 = bez limita). Kad se dostigne, aplikacija odbija nove AI pozive s jasnom porukom dok se limit ne poveća ili ne počne novi mjesec. „Provjeri vezu” radi i tada.
4. **Evidencija potrošnje kroz MEVAN:** broj poziva te ulazni i izlazni tokeni za tekući mjesec (UTC), prikazani u dijelu „AI servis”.
5. **Test ispravnosti skripti:** svaka skripta na svim ekranima provjerava se kao ispravan JavaScript.

## Šta aplikacija ne može prikazati

Stanje kredita kod AI servisa. Koliko je iz dostupnih izvora poznato, Anthropic to stanje ne izlaže kroz API (vidi se samo u konzoli, Settings → Billing), a ključ kojim aplikacija poziva model nema pristup podacima o naplati. Zato aplikacija prikazuje vlastitu evidenciju i vlastiti limit, a ne stanje računa.

## AI ključ i prijava

Ključ i postavke AI servisa pripadaju instanci aplikacije, ne korisniku: važe za svakoga ko se prijavi. Aplikacija trenutno ima jedan nalog za prijavu.

## Ograničenja

- Mjesečni limit broji pozive, ne novac; jedna integrisana analiza troši mnogo više od jednog nacrta po modulu.
- Tokeni se bilježe onako kako ih servis vrati; ako ih servis ne vrati, bilježi se poziv s nula tokena.
- Model koji ne podržava odabranu dubinu razmišljanja odbiće zahtjev; „Provjeri vezu” tada prikazuje poruku servisa.
- Evidencija je u bazi aplikacije; ako hosting nema trajni disk, briše se s novim deployem.

## Provjere

- `pytest`: 252 prolaza (247 ranijih + 5 novih): razmišljanje se čuva i šalje samo Claudeu, potrošnja se broji i limit zaustavlja pozive (i u pozadinskom poslu), stara baza dobija nove kolone, svako AI dugme prvo upozorava, sve skripte su ispravan JavaScript.
- Browser prolaz: izbor razmišljanja vidljiv samo za Claude, čuvanje, prikaz potrošnje, prozor upozorenja na bosanskom i engleskom, „Odustani” ne pokreće analizu, potvrda je pokreće.
- Oba mobilna toka i Word QA 12/12 prolaze.

## Šta nije testirano

Stvarni poziv Anthropic servisu s parametrom razmišljanja nije izvršen iz razvojnog okruženja. Render nije testiran.
