# Sedmi paket — 11.11.2026. (izgled zaključanih izvještaja, meni na niskom ekranu)

Osnova: šesti paket s dopunom 6.1. Mijenja se samo izgled. Sadržaj izvještaja, obračuni, zaključavanje, manifest, API i baza nisu mijenjani.

## Šta je promijenjeno

1. **„Odjava” je uvijek vidljiva.** Meni sada staje u visinu ekrana ispod zaglavlja, a donji dio („Podaci i sigurnost”, „Odjava”) ostaje prikovan dok se stavke iznad pomjeraju. Ranije je dno menija na nižim ekranima bilo ispod ruba.
2. **Zaključani izvještaji (Direktorski i Detaljni, PDF i Word)** imaju novi izgled:
   - zaglavlje i podnožje na svakoj strani, s brojem strane („Strana 2 / 14”);
   - naslovni blok: vrsta izvještaja, naziv kompanije, dijagnostika i četiri podatka o snimku u jednom redu;
   - numerisana poglavlja (01–06), naslovi u serifnom pismu, tekst u bezserifnom;
   - tri prioriteta s velikim brojevima; odabrani prioritet je označen;
   - zrelost po oblastima kao trake s ispisanom vrijednošću (umjesto radara); neocjenjiva oblast nema traku i piše „Neocjenjivo”, nikad nula;
   - finansijski scenariji u tabeli (PDF);
   - u detaljnom izvještaju kriteriji su grupisani po oblastima, a ocjena je prikazana i brojem i s pet polja.
3. **Fontovi su u repozitoriju** (`fonts/`: Source Sans 3 i Source Serif 4, licenca SIL OFL 1.1, tekst u `fonts/OFL-LICENSE.md`, 1,1 MB). PDF zato izgleda isto na svakom serveru i naša slova (č, ć, ž, š, đ) ne zavise od fontova instaliranih na serveru. Ako direktorij nedostaje, koristi se raniji sistemski font. `Dockerfile` kopira i `fonts/`.
4. **Pregled za štampu** („Kratki pregled”, „Detaljni pregled”) koristi isti stil naslova, linija i boja.
5. Vrijeme zaključavanja se prikazuje kao `11.11.2026. 09:48` uz oznaku „Zaključano (UTC)” (ranije ISO zapis).

## Šta nije mijenjano

- Svi tekstovi i podaci iz ranijeg izvještaja su i dalje u njemu; DEMO oznaka je na svakoj strani i u zaglavlju i podnožju Word dokumenta.
- Word izvoz sa stranice „Izvještaji” („Word · sažetak / detaljno”), Word izvoz integrisane analize i izvještaj projekta nisu mijenjani u ovom paketu.
- U Wordu se koriste fontovi Georgia i Calibri s računara čitaoca, jer se u Word dokument fontovi ne ugrađuju.

## Provjere

- `pytest`: 203 prolaza (196 ranijih + 7 novih u `tests/test_package7_reports.py`): fontovi i rezerva bez njih, zaglavlje/podnožje i broj strane na svakoj strani, neocjenjiva oblast nije nula, najduži dozvoljeni tekstovi (6000 znakova po polju) prelaze preko strana, Word zadržava tekst u pasusima i jedan grafikon, meni.
- Oba mobilna browser toka (odobrenje, četiri izvoza, čitanje PDF i Word sadržaja) i Word QA 12/12 prolaze.
- Vizuelno pregledano: direktorski i detaljni PDF (DEMO i stvarni način, s neocjenjivom oblašću), Word verzija otvorena u LibreOfficeu, meni na 1366×560 i 390×560, pregled za štampu.

## Granice

Word verzija nije otvorena u Microsoft Wordu (samo LibreOffice, koji zamjenjuje Georgia i Calibri sličnim fontovima). Render nije testiran. Safari i Firefox nisu testirani.
