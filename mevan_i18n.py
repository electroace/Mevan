"""Jezik interfejsa: bosanski (izvorni) i engleski.

Izvorni tekst je ključ, kao kod gettexta: `EN[bosanski tekst] = engleski tekst`. Server prevodi meni,
zaglavlje i prijavu; isti rječnik se šalje stranici, gdje zajednička skripta prevodi fiksne natpise
(dugmad, naslove, natpise polja). Tekst bez prevoda ostaje na bosanskom, pa se rječnik može dopunjavati
postepeno. Tekst koji unese korisnik se ne prevodi.
"""
import json

LANGS = ('bs', 'en')
DEFAULT = 'bs'
COOKIE = 'mevan_lang'

EN = {
    # zaglavlje, meni, prijava
    'Meni': 'Menu', 'Glavni meni': 'Main menu', 'Prijavljeni korisnik': 'Signed in as', 'Odjava': 'Sign out',
    '61 kriterij · 5 dimenzija': '61 criteria · 5 dimensions', 'Jezik': 'Language',
    'Kompanija': 'Company', 'Procjena': 'Assessment', 'Analiza i izvještaji': 'Analysis & reports', 'Projekti': 'Projects',
    'Kompanije i dijagnostike': 'Companies & diagnostics', 'Profil kompanije': 'Company profile', 'Pregled': 'Overview',
    'Finansije': 'Finance', 'Operacije': 'Operations', 'Planiranje i Supply Chain': 'Planning & Supply Chain',
    'Ljudi i liderstvo': 'People & Leadership', 'Sistem upravljanja': 'Management System', 'Finansijski efekti': 'Financial effects',
    'Vođeno prikupljanje': 'Guided collection', 'Vođeno prikupljanje i završni izvještaji': 'Guided collection and final reports',
    'Integrisana analiza (AI)': 'Integrated analysis (AI)', 'Analiza i odobravanje': 'Analysis & approval', 'Izvještaji': 'Reports',
    'Plan 90 dana': '90-day plan', 'Pregled portfolija': 'Portfolio overview', 'Podaci i sigurnost': 'Data & security',
    'MEVAN – prijava': 'MEVAN – sign in', 'Prijava': 'Sign in', 'Privatni demonstracijski pristup': 'Private demo access',
    'E-mail': 'Email', 'Lozinka': 'Password', 'Prijavi se': 'Sign in',
    'Pogrešna prijava. Provjerite e-mail i lozinku pa pokušajte ponovo.': 'Sign-in failed. Check your email and password and try again.',
    # prozori i poruke
    'Potvrda': 'Confirm', 'Potvrdi': 'Confirm', 'Odustani': 'Cancel', 'Unos': 'Input', 'Sačuvaj': 'Save', 'Zatvori poruku': 'Dismiss message',
    'Ukloni': 'Remove', 'Odobri': 'Approve', 'Nastavi': 'Continue', 'Obriši': 'Delete', 'Uvezi': 'Import', 'Učitaj': 'Load', 'Poveži': 'Link',
    'Dodaj kompaniju': 'Add company', 'Dodaj dijagnostiku': 'Add diagnostic', 'Nova kompanija': 'New company', 'Nova dijagnostika': 'New diagnostic',
    'Naziv nove kompanije': 'Name of the new company', 'Naziv nove dijagnostike': 'Name of the new diagnostic',
    'Sačuvano na serveru': 'Saved to server', 'Učitano sa servera': 'Loaded from server', 'Čeka sinhronizaciju': 'Waiting to sync',
    'Nema veze sa serverom': 'No connection to server', 'Učitavanje…': 'Loading…',
    # dijagnostika: dugmad
    '+ Novi finansijski nalaz': '+ New financial finding', 'Nacrt po pravilima': 'Rule-based draft', 'AI nacrt (server)': 'AI draft (server)',
    'Odobri demo': 'Approve demo', '+ Nova kompanija': '+ New company', '+ Nova dijagnostika': '+ New diagnostic', 'Otvori': 'Open',
    'Vrati METALPRO simulaciju': 'Restore METALPRO simulation', 'Otvori modul': 'Open module', 'Izvještaj modula': 'Module report',
    'Kratki pregled': 'Short preview', 'Detaljni pregled': 'Detailed preview', 'Word · sažetak': 'Word · summary', 'Word · detaljno': 'Word · detailed',
    '+ Dodaj aktivnost': '+ Add activity', 'Izvezi JSON kopiju': 'Export JSON copy', 'Uvezi JSON kopiju': 'Import JSON copy',
    'Obriši lokalne podatke': 'Delete local data', 'Vrati': 'Restore', 'Preuzmi JSON': 'Download JSON', 'Sačuvaj AI postavke': 'Save AI settings',
    'Provjeri vezu': 'Test connection', 'Ukloni ključ': 'Remove key', 'Štampaj / sačuvaj PDF': 'Print / save as PDF',
    'Kopiraj AI nacrt': 'Copy AI draft', 'Kopiraj prijedlog odluka': 'Copy proposed decisions', 'Stručni pregled': 'Expert review',
    'Dopuni osnovice i dokaze': 'Complete baselines and evidence', 'Konsultantska provjera i završni izvještaji': 'Consultant review and final reports',
    'Word · Detaljni izvještaj': 'Word · Detailed report', 'Pređi na izbor operativnog projekta': 'Go to operational project selection',
    'Pokreni kompletnu dijagnostiku': 'Run full diagnostic', 'Pokreni integrisanu analizu': 'Run integrated analysis', 'Analiza u toku…': 'Analysis in progress…',
    'Prikaži sve kriterije (brzi unos)': 'Show all criteria (quick entry)', 'Vođeni unos, jedno pitanje': 'Guided entry, one question',
    '← Prethodno': '← Previous', 'Sljedeće →': 'Next →',
    # dijagnostika: naslovi
    'Registar finansijskih efekata': 'Financial effects register', 'Analiza i korisničko odobravanje': 'Analysis and user approval',
    'Plan transformacije – 90 dana': 'Transformation plan – 90 days', 'Kontrola kvaliteta unosa': 'Entry quality check',
    'Historija dijagnostika': 'Diagnostic history', 'Demo podaci': 'Demo data', 'Simulirani finansijski potencijal': 'Simulated financial potential',
    'Sigurnosna kopija na serveru': 'Server backup', 'AI servis': 'AI service', '90-dnevni plan': '90-day plan', 'Ukupna dijagnostika': 'Overall diagnostic',
    'Ukupni MEVAN izvještaj': 'Overall MEVAN report', 'Obuhvat i zrelost': 'Coverage and maturity',
    'Prioritetni rizici – zahtijevaju neposrednu provjeru': 'Priority risks – require immediate review', 'Tri predložene upravljačke odluke': 'Three proposed management decisions',
    'Plan provjere 30/60/90 dana': '30/60/90-day verification plan', 'Jedinstveni izvršni pregled': 'Single executive overview',
    'Sistemski nalazi': 'Systemic findings', 'Direktorske odluke i KPI': 'Executive decisions and KPIs', 'Finansijski registar': 'Financial register',
    'Potvrđeni kriteriji': 'Confirmed criteria', 'Indeks zrelosti': 'Maturity index', 'Završeni moduli': 'Completed modules',
    # dijagnostika: polja i izbori
    'Opis': 'Description', 'Kategorija': 'Category', 'Godišnji potencijal (KM)': 'Annual potential (KM)', 'Jednokratni efekat (KM)': 'One-off effect (KM)',
    'Status': 'Status', 'Preklapanje sa ID nalaza': 'Overlaps with finding ID', 'Osnovica (broj)': 'Baseline (number)', 'Ciljna vrijednost (broj)': 'Target value (number)',
    'Vrijednost po jedinici (KM)': 'Value per unit (KM)', 'Period i izvor osnovice': 'Baseline period and source', 'Dokaz / pretpostavka': 'Evidence / assumption',
    'Uredivi nacrt zaključaka i preporuka': 'Editable draft of conclusions and recommendations', 'Aktivna kompanija': 'Active company',
    'Aktivna dijagnostika': 'Active diagnostic', 'Primjenjivo': 'Applicable', 'Status dokaza': 'Evidence status', 'Ocjena 0–5': 'Score 0–5',
    'KPI / izmjerena vrijednost': 'KPI / measured value', 'Potrebni dokazi i preporučeni izvori': 'Required evidence and recommended sources',
    'Obrazloženje za N/P': 'Reason for N/A', 'N/P potvrdio konsultant': 'N/A confirmed by consultant',
    'Nalaz i hipoteza o uzroku (uzrok nije automatski potvrđen)': 'Finding and cause hypothesis (the cause is not automatically confirmed)',
    'Finansijski efekat (opis i pretpostavke)': 'Financial effect (description and assumptions)', 'Preporuka': 'Recommendation',
    'Vraćanje iz sigurnosne kopije': 'Restore from backup', 'Servis': 'Service', 'Model': 'Model', 'Adresa servisa (https)': 'Service address (https)', 'API ključ': 'API key',
    'Hipoteza / nepotvrđeno': 'Hypothesis / unconfirmed', 'U provjeri': 'Under review', 'Stručno potvrđeno': 'Expert-confirmed', 'Da': 'Yes',
    'Nije primjenjivo (obrazložiti)': 'Not applicable (give a reason)', 'Nije provjereno': 'Not verified', 'Potvrđeno': 'Confirmed',
    'Dokaz nedostupan': 'Evidence unavailable', 'Nepoznato / još nije ocijenjeno': 'Unknown / not yet scored',
    'Scenarij': 'Scenario', 'Vrsta': 'Type', 'Godišnje (KM)': 'Annual (KM)', 'Jednokratno (KM)': 'One-off (KM)',
    'Direktna ušteda': 'Direct saving', 'Izbjegnuti trošak': 'Avoided cost', 'Dodatna kontribucija': 'Additional contribution',
    'Oslobođeni obrtni kapital': 'Released working capital', 'Naziv kompanije': 'Company name', 'Djelatnost': 'Industry', 'Sjedište': 'Head office',
    'Broj zaposlenih': 'Number of employees', 'Godišnji prihod (KM)': 'Annual revenue (KM)', 'ERP sistem': 'ERP system', 'Kontakt osoba': 'Contact person',
    'Aktivnost': 'Activity', 'Odgovorna osoba': 'Owner', 'Rok': 'Due date', 'Vrijednost': 'Value',
    # projekti
    'Osvježi': 'Refresh', 'Prikaži kandidate iz JSON-a': 'Show candidates from JSON', 'Sačuvaj ocjene na server': 'Save scores to server',
    'Učitaj ocjene sa servera': 'Load scores from server', 'Prikaži rangiranje C1–C3': 'Show ranking C1–C3', 'Generiši AI nacrt': 'Generate AI draft',
    'Preliminarni nacrt bez AI': 'Preliminary draft without AI', 'Kreiraj nacrt': 'Create draft', 'Izvezi Word': 'Export Word', 'Izvezi PDF': 'Export PDF',
    '+ Dodaj KPI': '+ Add KPI', '+ Dodaj korist u svaki scenarij': '+ Add benefit to each scenario', 'Izračunaj': 'Calculate',
    'Sačuvaj scenarije': 'Save scenarios', 'Sačuvaj nacrt': 'Save draft', 'Odobri fazu validacije': 'Approve validation phase',
    'Odobri implementaciju': 'Approve implementation', 'Evidentiraj efekat': 'Record effect', 'Sačuvaj sedmični pregled': 'Save weekly review',
    'Odaberite projekat': 'Select a project', 'Ostvareni finansijski efekti · evidencija': 'Realised financial effects · record',
    'Sedmični pregled projekta': 'Weekly project review', 'Iz dijagnostike u projekat': 'From diagnostic to project', 'Novi nacrt': 'New draft',
    'Projektne aktivnosti': 'Project activities', 'KPI registar': 'KPI register', 'Finansijski scenariji · procjene': 'Financial scenarios · estimates',
    'Kontrolne potvrde konsultanta': 'Consultant control confirmations', 'Registar efekata': 'Effects register', 'Aktivnosti': 'Activities',
    'KPI mjerenja': 'KPI measurements', 'Historija sedmica': 'Weekly history', 'Analiza v3 (JSON)': 'Analysis v3 (JSON)',
    'Identifikator kompanije': 'Company identifier', 'Identifikator dijagnostike': 'Diagnostic identifier', 'Naziv projekta': 'Project name',
    'Problem': 'Problem', 'Cilj': 'Objective', 'Obim': 'Scope', 'Metodologija': 'Methodology', 'Pretpostavke (jedna po redu)': 'Assumptions (one per line)',
    'Obavezne provjere (jedna po redu)': 'Required checks (one per line)', 'Period (npr. 2026-11)': 'Period (e.g. 2026-11)', 'Naziv efekta': 'Effect name',
    'Iznos (KM)': 'Amount (KM)', 'Referenca dokaza': 'Evidence reference', 'Vlasnik izvornog podatka': 'Source data owner',
    'Metoda obračuna i period (najmanje 10 znakova)': 'Calculation method and period (at least 10 characters)',
    'Oznaka zasebnog događaja (opcionalno)': 'Separate event tag (optional)', 'Sedmica (ISO format)': 'Week (ISO format)',
    'Prepreke (jedna po redu)': 'Blockers (one per line)', 'Odluke (jedna po redu)': 'Decisions (one per line)', 'Napomena': 'Note',
    'Napredno: ručni JSON unos': 'Advanced: manual JSON entry', 'Finansijski efekti — JSON lista (nepotvrđeni)': 'Financial effects — JSON list (unconfirmed)',
    'Operativna ušteda': 'Operating saving', 'Kontribucijska marža': 'Contribution margin', 'Jednokratni obrtni kapital': 'One-off working capital',
    'Obrtni kapital — jednokratno': 'Working capital — one-off', 'Ukloni korist': 'Remove benefit', 'Rangiranje projektnih kandidata': 'Project candidate ranking',
    'Još nema projekata': 'No projects yet', 'Nema projektnih aktivnosti u Charteru.': 'No project activities in the charter.', 'Nema KPI u Charteru.': 'No KPIs in the charter.',
    'Naziv aktivnosti': 'Activity name', 'Naziv KPI': 'KPI name', 'Nije započeto': 'Not started', 'Rok / sedmica': 'Due date / week',
    'Očekivani rezultat': 'Expected result', 'Kriterij prihvatanja': 'Acceptance criterion', 'Formula': 'Formula', 'Izvor podataka': 'Data source',
    'Početno stanje': 'Baseline', 'Predloženi cilj': 'Proposed target', 'Učestalost': 'Frequency', 'U toku': 'In progress', 'Završeno': 'Done', 'Blokirano': 'Blocked',
    'Početno stanje provjereno': 'Baseline verified', 'KPI ciljevi odobreni': 'KPI targets approved', 'Obavezne provjere završene': 'Required checks completed',
    # portfolio
    'Sve kompanije': 'All companies', 'Svi statusi': 'All statuses', 'Nacrt': 'Draft', 'Validacija': 'Validation', 'Implementacija': 'Implementation',
    'Zatvoreno': 'Closed', 'Nema projekata za odabrani filter.': 'No projects match the selected filter.', 'Otvori projektni modul': 'Open project module',
    'Kompanije': 'Companies', 'U implementaciji': 'In implementation', 'S potencijalno zakašnjelim rokovima': 'With potentially overdue deadlines',
    # vođeno prikupljanje
    'Pripremi METALPRO DEMO primjer': 'Prepare METALPRO DEMO example', 'Sačuvaj i nastavi': 'Save and continue',
    'Preuzmi AI prijedlog za pregled': 'Use AI proposal for review', 'Sačuvaj odabrani projektni nacrt': 'Save selected project draft',
    'Sačuvaj radnu reviziju': 'Save working revision', 'Odobri pregledanu reviziju': 'Approve reviewed revision', 'Konsultantska provjera': 'Consultant review',
    'Odobrene revizije': 'Approved revisions', 'Dokazi za ocjene': 'Evidence for scores', 'Provjera rizika': 'Risk review',
    'Sažetak, prioriteti i plan': 'Summary, priorities and plan', 'Odabrani projekat iz tri prioriteta': 'Selected project from the three priorities',
    'Način izvještaja': 'Report mode', 'Korak vođenog prikupljanja': 'Guided collection step', 'Prioritet za projekat': 'Priority for the project',
    'Vlasnik aktivnosti': 'Activity owner', 'Početak plana': 'Plan start', 'KPI i način potvrde početnog stanja': 'KPI and how the baseline is confirmed',
    'Stvarni konsultantski pregled': 'Real consultant review', 'DEMO — simulirani podaci': 'DEMO — simulated data',
    '1. Intervju': '1. Interview', '2. Dokumenti': '2. Documents', '3. Obilazak': '3. Site visit', '4. Dokazi i ocjene': '4. Evidence and scores',
    '5. Tri prioriteta': '5. Three priorities', '6. Odabrani projekat': '6. Selected project', '7. Plan za 90 dana': '7. 90-day plan',
    'Prvi prioritet': 'First priority', 'Drugi prioritet': 'Second priority', 'Treći prioritet': 'Third priority',
    'Još nema odobrenih revizija.': 'No approved revisions yet.', 'Otvorite konsultantsku provjeru iz odabrane dijagnostike.': 'Open the consultant review from a selected diagnostic.',
    'Potvrdi N/P kao prijavljeni konsultant': 'Confirm N/A as the signed-in consultant', 'Nije primjenjivo': 'Not applicable',
    'Samoprocjena': 'Self-assessment', 'Dokumentovano, čeka provjeru': 'Documented, awaiting review', 'Provjeren dokaz': 'Verified evidence',
    'Pregledano': 'Reviewed', 'Rizik prihvaćen': 'Risk accepted', 'Zaključi DEMO snimak': 'Lock DEMO snapshot',
}


def lang_of(request):
    value = request.cookies.get(COOKIE, '')
    return value if value in LANGS else DEFAULT


def t(lang, text):
    return EN.get(text, text) if lang == 'en' else text


def client_script(lang):
    """Jezik i rječnik za zajedničku skriptu. Na bosanskom se rječnik ne šalje."""
    words = json.dumps(EN if lang == 'en' else {}, ensure_ascii=False).replace('</', '<\\/')
    return f'<script id="mevan-i18n">window.MV_LANG={json.dumps(lang)};window.MV_I18N={words};</script>'
