# MEVAN 4.0 — razvojni korak 4 (TEST)

Novo: `project_ai_pack.py` i `POST /api/v4/project-ai-pack`.

- Endpoint koristi postojeću prijavu i provjeru porijekla zahtjeva.
- Polazi od rangiranog kandidata iz `project_planner.py`, a AI generiše strukturirani nacrt metodologije, aktivnosti, isporuka, kriterija prihvatanja, KPI i rizika.
- Pydantic odbija nepoznata polja i numeričke baseline/ciljeve u AI izlazu.
- Poslovna pravila servera ponovo postavljaju `baseline_verified`, `targets_approved`, `checks_completed` na `false`, a finansijske efekte na praznu listu.
- Endpoint NE kreira automatski projekat u bazi. Konsultant može pregledati odgovor i potom poslati izmijenjeni `company_id`, `diagnostic_id`, `title`, `charter` na postojeći `POST /api/v4/projects`.
- Pozivanje stvarnog OpenAI API-ja nije testirano; testirana je simulirana AI komunikacija. Potreban je `OPENAI_API_KEY`.
- Nema još UI editora, finansijskog modela, Word/PDF izvoza niti završnog METALPRO testa. NE POSTAVLJATI na Render.

Test: `python -m unittest discover -p 'test_*.py' -v`.
