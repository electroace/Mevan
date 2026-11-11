# Korak 23 — udaljeni testni acceptance gate

Dodana je read-only skripta `remote_acceptance.py` koja provjerava da HTTPS testna instanca ne otkriva glavne ekrane i workspace API neprijavljenom korisniku. Nema kredencijala, slanja podataka ni izmjena baze.

Pokretanje **tek nakon postavljanja izolovane testne instance**:

`python remote_acceptance.py https://TVOJA-TESTNA-ADRESA`

**Ne pokretati na produkciji.** Prije testne implementacije: izolovana grana `mevan-v2-test`, zasebna baza, novi tajni ključevi, backup, HTTPS. Udaljeni test sam po sebi ne dokazuje funkcionalnost prijave, AI, preglednika ili poslovnog toka. Testna instanca još nije postavljena.
