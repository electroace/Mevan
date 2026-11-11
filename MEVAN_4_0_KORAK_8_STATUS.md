# Korak 8 — Finansijski scenariji (TEST)

Dodan deterministički kalkulator tri scenarija: pesimistični, realni i optimistični. Godišnje operativne koristi i jednokratno oslobađanje obrtnog kapitala vode se odvojeno. ROI i jednostavni povrat koriste samo neto godišnji efekat i trošak implementacije. Svi efekti su **procjene**, potvrđeni efekti ostaju 0. Kalkulator ne mijenja bazu niti odobrava finansije.

Endpoint: `POST /api/v4/financial-scenarios/calculate` uz prijavu i CSRF/origin zaštitu. Nisu završeni finansijski UI, evidencija ostvarenih efekata i PDF/Word izvoz.
