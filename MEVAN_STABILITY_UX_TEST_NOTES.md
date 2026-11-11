# MEVAN 4.0 — Stability & UX testni paket

Osnova: prethodni TEST24 FIX, bez izmjena produkcijske grane.

Uključeno:
- Lokalni autosave i povrat procjena kandidata nakon F5 (iz prethodnog TEST24 paketa). Nije serversko čuvanje.
- Širi projektni panel i prilagođen prikaz za uske ekrane.
- Opisni orijentiri za pet faktora projektnih procjena (0/3/5), bez promjene algoritma bodovanja.
- Višeredna obrazloženja i minimalno 15 znakova za uključivanje kandidata u projektni nacrt.
- Preciznije upozorenje za neprovjerene dokaze u dijagnostici.
- Ujednačen naziv integrisane dijagnostike u interfejsu na MEVAN 4.0.

Nije uključeno:
- Serversko čuvanje nedovršenih procjena.
- Specifične skale za svih 61 kriterij.
- Redizajn DOCX/PDF izvještaja.
- Nezavisna finansijska validacija.

Provjera: 38 automatskih Python testova prošlo; JavaScript sintaksa oba HTML ekrana prošla. Browser test nakon Render objave tek slijedi.
