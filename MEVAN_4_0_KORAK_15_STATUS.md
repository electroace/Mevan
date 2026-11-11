# MEVAN 4.0 — Korak 15: METALPRO DEMO (offline integracijski test)

- Sintetička dijagnostika svih 61 kriterija: 61 dokumentovana samoprocjena, 0 nezavisno verificiranih; indeks 36,4/100.
- Dimenzije: F 38,3; O 34,7; P 35,0; L 42,0; M 33,3.
- Ispravljena integracija: kandidatni modul čita i `priority_decisions` i `criteria` iz postojećeg dijagnostičkog engine-a.
- METALPRO test preko autentificiranih HTTP ruta: kandidati → rangiranje → preliminarni nacrt → pohrana → blokada implementacije bez dokaza → validacija → scenariji → blokada sedmičnog unosa i efekata prije implementacije → Word/PDF → dashboard.
- Realni scenarij (SIMULIRANO): godišnje bruto koristi 52.167 KM, jednokratno oslobađanje obrtnog kapitala 160.000 KM; dodatni godišnji troškovi 2.500 KM i jednokratna implementacija 15.000 KM su samo demo pretpostavke. Potvrđeni efekti 0 KM.
- 38 automatskih testova prošlo. Nije testirano u browseru, na Renderu ni sa stvarnim OpenAI API pozivom.
- Test **ne** odobrava implementaciju na izmišljenim dokazima, ne kreira lažne sedmične rezultate, ne potvrđuje finansijske efekte. Puni realni poslovni ciklus tek treba testirati sa stvarnim podacima i konsultantskim odobrenjima.
- Produkcijski `main` nije diran; ZIP je samo razvojni paket.

Pokretanje: `python -m pytest -q` i `python metalpro_demo.py`.
