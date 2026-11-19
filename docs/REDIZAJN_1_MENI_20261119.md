# Redizajn 1 — 19.11.2026.: meni po koracima rada i kontekst u zaglavlju

Grana: `mevan-v2-test`. Mijenja se raspored menija i zaglavlje. Poslovna logika, podaci, API i izvještaji nisu mijenjani; METALPRO DEMO i model 61/5 su nepromijenjeni (test iz faze 0 prolazi).

## Šta je promijenjeno

1. **Meni ima šest numerisanih koraka** umjesto četiri grupe po funkcijama: 1 Kompanija, 2 Procjena, 3 Nalazi, 4 Finansije, 5 Opcije i plan, 6 Izvještaji. „Podaci i sigurnost” i „Odjava” ostaju prikovani na dnu.
2. **Sve stranice su u meniju.** „Lanac nalaza” i „Projektne opcije” (model 65/6) više se ne otvaraju samo dugmadima na Pregledu.
3. **Meni prikazuje samo ono što važi za aktivnu dijagnostiku.** Za 65/6: Lanac nalaza i Projektne opcije; za 61/5: Integrisana analiza (AI), Projekti, Pregled portfolija i Vođeno prikupljanje. Stavke zajedničke za oba modela su uvijek vidljive.
4. **Zaglavlje prikazuje kontekst rada:** birač kompanije ▸ birač dijagnostike, oznaka modela (61/5 ili 65/6 nacrt) i oznaka DEMO. Promjena izbora odmah otvara tu dijagnostiku. Slogan i „61 kriterij · 5 dimenzija” su uklonjeni.
5. **„Premium PDF (nacrt)” je i na stranici „Izvještaji”** za dijagnostike 65/6.
6. Kutije s brojkama na stranicama 65/6 (nalazi, pouzdanost, finansije) sada stoje u redu, kao na Pregledu; ranije su se slagale jedna ispod druge.

## Šta je ostalo isto

Nazivi stavki, njihove adrese i oznake stranica nisu mijenjani, pa postojeći linkovi i testovi tokova rade. Žuta DEMO traka na vrhu stranice je i dalje tu. Na telefonu se birači u zaglavlju ne prikazuju (nema mjesta); izbor ostaje na stranici „Kompanije i dijagnostike”.

## Šta nije urađeno (naredni koraci redizajna)

Pregled kao kontrolna tabla, lakša kartica kriterija, čitljivi tekstovi umjesto tehničkih oznaka, premještanje podešavanja u korisnički meni i zamjena žute DEMO trake malom oznakom.

## Provjere

- `pytest`: 387 prolaza (381 raniji + 6 novih u `tests/test_redesign_menu.py`); tri ranija testa su prilagođena novom rasporedu grupa (provjeravaju iste stavke).
- Browser prolaz na 1366 px i 390 px: meni za 61/5 i za 65/6 prikazuje očekivane stavke; „Lanac nalaza” iz menija računa nalaze; izbor dijagnostike u zaglavlju mijenja dijagnostiku i meni; ostala tri ekrana prikazuju meni modela 61/5; bez horizontalnog pomjeranja i bez JavaScript grešaka.
- Završni browser prolaz 65/6 iz faze 7, oba postojeća mobilna toka i Word QA 12/12 prolaze.

Render nije testiran.
