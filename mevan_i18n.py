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


# ---- korak 2: objašnjenja, upozorenja i poruke
EN.update({
    # zajedničko
    'DEMO — simulirani podaci. Nije stvarno konsultantsko odobrenje niti provjera dokaza.': 'DEMO — simulated data. Not a real consultant approval or evidence check.',
    'Prvi unos – METALPRO demo': 'First entry – METALPRO demo', 'Učitana pregledana serverska revizija': 'Reviewed server revision loaded',
    'Greška sinhronizacije – izvezi JSON kopiju': 'Sync error – export a JSON copy', 'Neocjenjivo': 'Not scorable', 'Nije procijenjeno': 'Not assessed',
    'Planiranje': 'Planning', 'Ljudi': 'People', 'Upravljanje': 'Management',
    # kompanije, profil, pregled
    'Lokalni radni prostor. Svaka kompanija ima zasebne procjene i historiju. Podaci se sinhronizuju sa privatnim serverom.': 'Local workspace. Each company has its own assessments and history. Data is synced with the private server.',
    'Privatni testni radni prostor. Dokazi i pristup stvarnim klijentima zahtijevaju zasebnu provjeru.': 'Private test workspace. Evidence and access for real clients require a separate review.',
    'Vraća izvornu METALPRO simulaciju i zamjenjuje sve lokalne podatke. Prije toga izvezite sigurnosnu kopiju.': 'Restores the original METALPRO simulation and replaces all local data. Export a backup first.',
    'Podaci se čuvaju na privatnom serveru i lokalno kao rezervna kopija.': 'Data is stored on the private server and locally as a backup copy.',
    'MEVAN Performance Excellence System · pregled procjene': 'MEVAN Performance Excellence System · assessment overview',
    # modul i kriterij
    'Upozorenja ne mijenjaju ocjene. Status „Potvrđeno“ je oznaka unosa konsultanta, a ne nezavisna verifikacija.': 'Warnings do not change scores. The “Confirmed” status is the consultant’s entry mark, not independent verification.',
    'kriterija bez potpune ocjene/dokaza ·': 'criteria without a complete score/evidence ·', 'N/P bez obrazloženja ·': 'N/A without a reason ·', 'mogućih neslaganja': 'possible inconsistencies',
    'Šta mjerimo:': 'What we measure:', 'Pokazatelj:': 'Indicator:', 'Dokazi koje treba tražiti:': 'Evidence to ask for:', 'Šta procjenjujemo:': 'What we assess:',
    'Referentni period i opseg provjere navedite uz dokaz. Skala 0–5 je opća smjernica; ocjenu potvrdite prema stvarnom stanju, ne prema pretpostavci.': 'State the reference period and review scope with the evidence. The 0–5 scale is a general guide; confirm the score against the actual situation, not an assumption.',
    'Ocjenjujte stvarno stanje za navedeni period i opseg; ako ne znate odgovor, ostavite „Nepoznato“, ne birajte nulu. Ocjena 5 zahtijeva dokaz kontinuiranog unapređenja.': 'Score the actual situation for the stated period and scope; if you do not know the answer, leave “Unknown” and do not choose zero. A score of 5 requires evidence of continuous improvement.',
    '0 — Proces ne postoji ili se ne provodi': '0 — The process does not exist or is not carried out', '1 — Povremena, neformalna praksa': '1 — Occasional, informal practice',
    '2 — Djelimično uvedeno, bez dosljednog praćenja': '2 — Partly introduced, without consistent tracking', '3 — Definisan proces koji se redovno provodi': '3 — A defined process that is carried out regularly',
    '4 — Proces se mjeri, analizira i koriguje': '4 — The process is measured, analysed and corrected', '5 — Standardizovan proces s dokazanim kontinuiranim unapređenjem': '5 — A standardised process with proven continuous improvement',
    'N/P zahtijeva konkretan razlog i imenovanu potvrdu konsultanta.': 'N/A requires a specific reason and a named consultant confirmation.',
    'Ocjena mora biti cijeli broj od 0 do 5.': 'The score must be a whole number from 0 to 5.', 'Za status Potvrđeno navedite izvor i period dokaza.': 'For Confirmed status, state the evidence source and period.',
    'Potvrđen odgovor zahtijeva ocjenu.': 'A confirmed answer requires a score.',
    'Ocjena je unesena, ali dokaz nije provjeren. Ocjena ostaje preliminarna dok se dokaz ne validira.': 'A score is entered but the evidence is not verified. The score stays preliminary until the evidence is validated.',
    'Obavezno za potvrdu: izvor, referentni period, dokument ili zapis': 'Required for confirmation: source, reference period, document or record',
    'Predložena intervencija:': 'Suggested intervention:',
    # finansijski efekti
    'Finansijski efekti su HIPOTEZE dok nisu potkrijepljeni dokumentima i stručno potvrđeni. Preklapanja se isključuju iz validiranih zbirnih iznosa. Obrtni kapital nije godišnja ušteda.': 'Financial effects are HYPOTHESES until supported by documents and expert-confirmed. Overlaps are excluded from validated totals. Working capital is not an annual saving.',
    'Potvrđene direktne godišnje uštede': 'Confirmed direct annual savings', 'Potvrđena dodatna kontribucija': 'Confirmed additional contribution', 'Potvrđen oslobođeni obrtni kapital': 'Confirmed released working capital',
    'Bez označenog preklapanja': 'No overlap marked', 'UPOZORENJE: potencijalno dvostruko računanje': 'WARNING: potential double counting', 'moguće dvostruko računanje': 'possible double counting',
    'Ukloniti nalaz?': 'Remove this finding?', 'Ukloni finansijski nalaz': 'Remove financial finding', 'Novi nalaz': 'New finding',
    # analiza i odobravanje, izvještaji, plan
    'Analiza po pravilima radi bez AI ključa. Generativni AI nacrt dostupan je samo kada je serverski servis konfigurisan. Svaki nacrt zahtijeva stručnu provjeru; odobravanje je i dalje demonstracijsko i nije namijenjeno stvarnim klijentima.': 'Rule-based analysis works without an AI key. A generative AI draft is available only when the server service is configured. Every draft requires expert review; approval is still a demonstration and is not intended for real clients.',
    'Tok rada: pripremi nacrt → stručno uredi → odobri simulaciju → izvezi Word. Svaka promjena ocjena, finansijskih efekata ili odobrenog teksta poništava važenje prethodnog odobrenja.': 'Workflow: prepare a draft → edit professionally → approve the simulation → export Word. Any change to scores, financial effects or the approved text invalidates the previous approval.',
    'Nacrt / nije odobreno': 'Draft / not approved', 'Interno odobren demo': 'Internally approved demo', 'Izmijenjeni podaci – potrebno ponovno odobrenje': 'Data changed – re-approval required',
    'Izvještaj nije odobren.': 'The report is not approved.', 'Odobreno:': 'Approved:', 'Prvo pripremite nacrt.': 'Prepare a draft first.',
    'Prije odobravanja završite sve primjenjive kriterije.': 'Complete all applicable criteria before approving.',
    'Odobriti isključivo INTERNI SIMULACIJSKI izvještaj? Ovo nije validacija stvarnih dokaza.': 'Approve an INTERNAL SIMULATION report only? This is not validation of real evidence.',
    'AI nacrt je pripremljen. Provjerite sve tvrdnje i uredite tekst prije odobravanja.': 'The AI draft is ready. Check every claim and edit the text before approving.', 'AI nacrt nije kreiran:': 'The AI draft was not created:',
    'Godišnji efekti (različite kategorije)': 'Annual effects (different categories)', 'Oslobađanje obrtnog kapitala': 'Working capital release', 'NEVALIDIRANO': 'NOT VALIDATED',
    'Efekti su ilustrativni, različitih tipova i zahtijevaju provjeru preklapanja i finansijskih pretpostavki. Oslobađanje gotovine nije prihod ni ušteda.': 'The effects are illustrative, of different types, and require a check of overlaps and financial assumptions. A cash release is neither revenue nor a saving.',
    'Dostupan je stvarni Word DOCX izvoz za pojedinačne module i ukupnu dijagnostiku. Demonstracijska analiza i interno odobravanje dostupni su u zasebnom modulu. Pravi AI i sigurne korisničke uloge zahtijevaju serversku aplikaciju.': 'A real Word DOCX export is available for individual modules and the overall diagnostic. Demonstration analysis and internal approval are available in a separate module. Real AI and secure user roles require the server application.',
    'Ovo je prototip. Finansijski iznosi su prikazani samo za izvornu METALPRO simulaciju. DOCX dokumenti su radni nacrti; bez provjerenih dokaza i stručnog odobrenja nisu validirana dijagnostika.': 'This is a prototype. Financial amounts are shown only for the original METALPRO simulation. DOCX documents are working drafts; without verified evidence and expert approval they are not a validated diagnostic.',
    'Unesite aktivnosti, odgovorne osobe, rokove i KPI.': 'Enter activities, owners, due dates and KPIs.', 'Ukloniti aktivnost iz plana?': 'Remove this activity from the plan?', 'Ukloni aktivnost': 'Remove activity',
    'Dozvolite otvaranje novog prozora.': 'Allow the new window to open.',
    # integrisana analiza
    'Radni nacrt. AI zaključci nisu nezavisno verificirani. Simulirani dokazi nisu stvarne potvrde; potrebna je stručna revizija prije upotrebe kod klijenta.': 'Working draft. AI conclusions are not independently verified. Simulated evidence is not real confirmation; expert review is required before client use.',
    'Potencijali nisu realizovane koristi. Obrtni kapital nije EBITDA. Svi iznosi i statusi dolaze iz kontrolnog mehanizma.': 'Potentials are not realised benefits. Working capital is not EBITDA. All amounts and statuses come from the control mechanism.',
    'Nezavisno potvrđeni godišnji efekti': 'Independently confirmed annual effects', 'Potvrđeni jednokratni efekti': 'Confirmed one-off effects', 'Scenariji na provjeri': 'Scenarios under review',
    'Nema unesenih scenarija.': 'No scenarios entered.', 'Iznosi su isključivo simulirani ili nepotvrđeni scenariji. Nisu ostvarene koristi, nisu odobreni i ne sabiraju se.': 'The amounts are simulated or unconfirmed scenarios only. They are not realised benefits, are not approved and are not added up.',
    'Prvo završite integrisanu dijagnostiku.': 'Complete the integrated diagnostic first.', 'Nije odabrana kompanija ili dijagnostika.': 'No company or diagnostic is selected.',
    'Prijenos nije uspio. Provjerite dozvole preglednika.': 'The transfer failed. Check the browser permissions.', 'Prvo pokrenite kompletnu dijagnostiku.': 'Run the full diagnostic first.',
    'Podaci su promijenjeni tokom analize. Ponovo pokrenite analizu.': 'The data changed during the analysis. Run the analysis again.',
    # podaci i sigurnost, AI servis
    'Ovaj demonstracijski prototip radi uz serversku prijavu i SQLite bazu; nije prošao produkcijsku sigurnosnu reviziju. Korisničke lozinke se ne ugrađuju u HTML. Kompanije i dijagnostike se sinhronizuju na server, a lokalna kopija ostaje u pregledniku. Nije pogodan za povjerljive podatke stvarnih klijenata.': 'This demonstration prototype runs with a server sign-in and an SQLite database; it has not passed a production security review. User passwords are not embedded in HTML. Companies and diagnostics are synced to the server, and a local copy stays in the browser. It is not suitable for confidential data of real clients.',
    'Preuzmite kopiju prije većih izmjena. Vraćanje prepisuje sve trenutno spremljene podatke i traži izričitu potvrdu.': 'Download a copy before major changes. Restoring overwrites all currently stored data and asks for explicit confirmation.',
    'Odaberite servis i unesite vlastiti API ključ. Ključ se čuva šifrovan na serveru, ne prikazuje se ponovo i nije dio sigurnosnih kopija. Kada pokrenete AI nacrt, podaci dijagnostike šalju se odabranom servisu.': 'Choose a service and enter your own API key. The key is stored encrypted on the server, is never shown again and is not part of backups. When you run an AI draft, the diagnostic data is sent to the selected service.',
    'AI servis nije podešen. Analiza po pravilima radi i bez ključa.': 'The AI service is not set up. Rule-based analysis works without a key.', 'Ostavite prazno da zadržite postojeći': 'Leave empty to keep the existing key',
    'AI postavke su sačuvane. Provjerite vezu prije prve upotrebe.': 'AI settings saved. Test the connection before first use.', 'AI postavke nisu sačuvane:': 'AI settings were not saved:',
    'Prvo sačuvajte postavke, pa provjerite vezu.': 'Save the settings first, then test the connection.', 'Veza radi. Model:': 'The connection works. Model:', 'Provjera veze nije uspjela:': 'The connection test failed:',
    'Ukloniti sačuvani API ključ i postavke AI servisa?': 'Remove the stored API key and AI service settings?', 'Ključ je uklonjen.': 'The key has been removed.', 'Ključ nije uklonjen:': 'The key was not removed:',
    'Postavke AI servisa nisu učitane:': 'AI service settings could not be loaded:', 'Odaberite JSON sigurnosnu kopiju.': 'Choose a JSON backup file.',
    'Vraćanje će PREPISATI sve trenutno spremljene podatke. Nastaviti?': 'Restoring will OVERWRITE all currently stored data. Continue?', 'Vraćanje sigurnosne kopije': 'Restore backup',
    'Za potvrdu upišite: VRATI-PODATKE': 'To confirm, type: VRATI-PODATKE', 'Vrati podatke': 'Restore data', 'Vraćanje nije uspjelo:': 'Restore failed:',
    'Podaci vraćeni. Stranica će se ponovo učitati.': 'Data restored. The page will reload.', 'Obrisati sve lokalne podatke?': 'Delete all local data?',
    'Ovo će zamijeniti sve lokalne podatke DEMO simulacijom. Prvo izvezite sigurnosnu kopiju. Nastaviti?': 'This will replace all local data with the DEMO simulation. Export a backup first. Continue?', 'Vrati simulaciju': 'Restore simulation',
    'Uvoz će zamijeniti sve lokalne podatke. Prvo izvezite postojeću kopiju. Nastaviti?': 'The import will replace all local data. Export the existing copy first. Continue?', 'Uvoz JSON kopije': 'Import JSON copy',
    'Sigurnosna kopija je uvezena.': 'The backup has been imported.', 'Uvoz nije uspio:': 'Import failed:',
    'Druga sesija je izmijenila radni prostor. Izvezite svoju lokalnu JSON kopiju prije ponovnog učitavanja.': 'Another session changed the workspace. Export your local JSON copy before reloading.',
    # projekti
    'Nacrti zahtijevaju odobrenje konsultanta · simulirani podaci nisu potvrđeni': 'Drafts require consultant approval · simulated data is not confirmed', 'TEST / DEMO.': 'TEST / DEMO.',
    'Ovaj ekran ne potvrđuje finansijske efekte niti verifikuje dokaze. Označavanje kontrolnih polja je izjava konsultanta, ne nezavisna verifikacija.': 'This screen does not confirm financial effects or verify evidence. Ticking the control boxes is the consultant’s statement, not independent verification.',
    'Nakon završene v3 dijagnostike kliknite „Pređi na izbor operativnog projekta“. Nalazi se prenose automatski. Ručni JSON ostaje samo za naprednu provjeru.': 'After the v3 diagnostic is complete, click “Go to operational project selection”. Findings are transferred automatically. Manual JSON remains only for advanced checks.',
    'Serversko čuvanje je ručno. Lokalna kopija ostaje sačuvana u pregledniku. Učitavanje sa servera traži potvrdu.': 'Saving to the server is manual. A local copy stays in the browser. Loading from the server asks for confirmation.',
    'Tri dugmeta ispod postaju aktivna kada se učitaju kandidati iz dijagnostike.': 'The three buttons below become active once candidates are loaded from the diagnostic.',
    'AI nacrt traži unesen API ključ (Dijagnostika → Podaci i sigurnost → AI servis). Bez ključa koristite preliminarni nacrt.': 'An AI draft needs an API key (Diagnostic → Data & security → AI service). Without a key, use the preliminary draft.',
    'Automatski AI paket generiše se kroz postojeći API. Ovaj ekran omogućava pregled i uređivanje spremljenih nacrta.': 'The automatic AI pack is generated through the existing API. This screen lets you review and edit saved drafts.',
    'Kreirajte novi nacrt ili otvorite postojeći.': 'Create a new draft or open an existing one.', 'Izvještaj uključuje samo sačuvane podatke. Prije izvoza sačuvajte promjene.': 'The report includes saved data only. Save your changes before exporting.',
    'Uredite aktivnosti u obrascu. Dodatna AI polja se čuvaju bez brisanja.': 'Edit activities in the form. Additional AI fields are kept and not deleted.', 'Cilj se ne smatra odobrenim dok ga konsultant ne potvrdi.': 'A target is not considered approved until the consultant confirms it.',
    'Tri scenarija. Godišnje koristi i jednokratno oslobađanje obrtnog kapitala računaju se odvojeno. Nema potvrđenih efekata.': 'Three scenarios. Annual benefits and the one-off working capital release are calculated separately. There are no confirmed effects.',
    'Implementacija se ne može odobriti bez sve tri potvrde. Odobreni projekat nije moguće uređivati bez nove verzije.': 'Implementation cannot be approved without all three confirmations. An approved project cannot be edited without a new version.',
    'Unos je izjava konsultanta na osnovu navedenog dokaza. Nije nezavisna verifikacija. Periodi se ne godišnje preračunavaju niti automatski sabiraju bez provjere preklapanja.': 'An entry is the consultant’s statement based on the stated evidence. It is not independent verification. Periods are not annualised or added up automatically without an overlap check.',
    'Konsultant je provjerio izvor i obračun (nije nezavisna verifikacija)': 'The consultant checked the source and the calculation (not independent verification)',
    'Odaberite status i unesite rezultat za svaku projektnu aktivnost.': 'Choose a status and enter the result for each project activity.',
    'Unesite izmjerene vrijednosti, period i izvor. Prazna vrijednost se ne prikazuje kao ostvarenje.': 'Enter the measured values, period and source. An empty value is not shown as an achievement.',
    'Sedmična evidencija je izvještaj konsultanta; ne predstavlja nezavisno potvrđene finansijske efekte.': 'The weekly record is the consultant’s report; it does not represent independently confirmed financial effects.',
    'Nacrt je sačuvan.': 'The draft has been saved.', 'Nacrt je kreiran; nije odobren za implementaciju.': 'The draft has been created; it is not approved for implementation.',
    'Potvrđujete da su početno stanje, KPI ciljevi i obavezne provjere stvarno provjereni?': 'Do you confirm that the baseline, KPI targets and required checks have actually been verified?', 'Potvrđujem': 'I confirm',
    'Sedmični pregled sačuvan kao evidencija konsultanta.': 'Weekly review saved as the consultant’s record.', 'Odaberite projekat': 'Select a project', 'Prvo odaberite projekat': 'Select a project first',
    'Scenariji izračunati — sve su procjene, ništa nije potvrđeno.': 'Scenarios calculated — all are estimates, nothing is confirmed.', 'Finansijski scenariji sačuvani kao procjene.': 'Financial scenarios saved as estimates.',
    'Projektni nacrt je sačuvan. Izbor i finansijski efekti nisu potvrđeni.': 'The project draft has been saved. The selection and financial effects are not confirmed.',
    'Ocijenite najmanje jednog kandidata.': 'Score at least one candidate.', 'Nema ocijenjenih kandidata.': 'No candidates have been scored.', 'Prvo učitajte kandidate.': 'Load the candidates first.',
    'Unesite identifikatore kompanije i dijagnostike.': 'Enter the company and diagnostic identifiers.', 'Serverski nacrt nije pronađen.': 'No server draft was found.',
    # portfolio i vođeno prikupljanje
    'Pregled projekata prijavljenog konsultanta. Procjene i potvrde nisu nezavisno verificirani rezultati.': 'Projects of the signed-in consultant. Estimates and confirmations are not independently verified results.',
    'Pregledajte izvore, period i trag provjere svakog kriterija. Ocjene se prenose iz odabrane dijagnostike.': 'Review the sources, period and audit trail of each criterion. Scores are carried over from the selected diagnostic.',
    'Plan za 90 dana dopunite prije kreiranja projektnog nacrta. Nacrt ne odobrava implementaciju ni finansijske efekte.': 'Complete the 90-day plan before creating the project draft. A draft does not approve implementation or financial effects.',
    'Za novo odobrenje: sažetak najmanje 80 znakova i 12 riječi, svaki prioritet 40 znakova i 6 riječi, svaki period plana 60 znakova i 10 riječi; najviše 6000 znakova po polju. Zamjenske oznake i ponavljanja nisu dovoljni. Ovo je tehnička provjera potpunosti, a stručni pregled ostaje obaveza konsultanta.': 'For a new approval: the summary needs at least 80 characters and 12 words, each priority 40 characters and 6 words, each plan period 60 characters and 10 words; at most 6000 characters per field. Placeholders and repetition are not enough. This is a technical completeness check; the expert review remains the consultant’s responsibility.',
    'Ulazne ocjene ili nalazi su promijenjeni. Pokrenuti novi pregled dokaza i plana? Prethodna odobrenja ostaju dostupna.': 'The input scores or findings have changed. Start a new review of evidence and plan? Previous approvals remain available.',
    'Pregled je zaustavljen. Ranija odobrenja možete preuzeti ispod.': 'The review was stopped. You can download earlier approvals below.',
    'Zaključati DEMO — simulirani podaci, bez stvarnog konsultantskog odobrenja?': 'Lock DEMO — simulated data, without a real consultant approval?',
    'Potvrđujete pregled dokaza, tri prioriteta i 90-dnevnog plana ove dijagnostike?': 'Do you confirm the review of evidence, the three priorities and the 90-day plan of this diagnostic?',
    'Odobri reviziju': 'Approve revision', 'Novi pregled': 'New review', 'Pokreni novi pregled': 'Start new review',
})

# ---- zaključani izvještaji (PDF i Word): fiksni natpisi; ključevi s {…} su obrasci za str.format
EN.update({
    'Direktorski izvještaj': 'Executive report', 'Detaljni stručni izvještaj': 'Detailed expert report', 'DEMO snimak': 'DEMO snapshot', 'Odobrenje': 'Approval',
    'Revizija': 'Revision', 'Pripremio': 'Prepared by', 'Konsultant': 'Consultant', 'Zaključano (UTC)': 'Locked (UTC)', 'Odabrani prioritet': 'Selected priority',
    'Nije odabran': 'Not selected', 'Projektni nacrt': 'Project draft', 'Nije povezan': 'Not linked', 'primjenjivo {a}, N/P {n}': 'applicable {a}, N/A {n}',
    '{v} KM jednokratno': '{v} KM one-off', '{v} KM godišnje': '{v} KM per year', 'Intervju': 'Interview', 'Dokumenti': 'Documents', 'Obilazak': 'Site visit',
    'Nije prikupljeno': 'Not collected', 'Izvor {s} · Period {a} – {b}': 'Source {s} · Period {a} – {b}', 'simulacija': 'simulation',
    'Simulirani procjenjivač': 'Simulated assessor', 'Procijenio': 'Assessed by', 'Trag': 'Audit trail', 'simulirani podaci': 'simulated data',
    'Primjenjivo {a}/61 · N/P {n}. N/P je isključen iz nazivnika; nepoznato nije ocjena nula.': 'Applicable {a}/61 · N/A {n}. N/A is excluded from the denominator; unknown is not a zero score.',
    '{c} · N/P · {r} · Potvrdio konsultant: {w}': '{c} · N/A · {r} · Confirmed by consultant: {w}',
    '1–30 dana': 'Days 1–30', '31–60 dana': 'Days 31–60', '61–90 dana': 'Days 61–90',
    'Neocjenjivo — nema ocijenjenih primjenjivih kriterija · {n} kriterija': 'Not scorable — no applicable criteria have been scored · {n} criteria',
    'Ukupni indeks {i}/100 · {n} kriterija': 'Overall index {i}/100 · {n} criteria', 'Strana': 'Page',
    'DEMO — simulirani podaci — nije stvarno konsultantsko odobrenje, provjera dokaza ili potvrda finansijskog efekta.': 'DEMO — simulated data — not a real consultant approval, evidence check or confirmation of a financial effect.',
    'DEMO — simulirani podaci — nije stvarni provjereni nalaz': 'DEMO — simulated data — not a real verified finding',
    'Sažetak konsultanta': 'Consultant summary', 'Tri prioriteta': 'Three priorities', 'Zrelost po oblastima': 'Maturity by area',
    'Nije primjenjivo — obuhvat i razlozi': 'Not applicable — scope and reasons', 'Finansijski potencijal': 'Financial potential', 'Plan za 90 dana': '90-day plan',
    'Ocjene i trag provjere dokaza': 'Scores and evidence audit trail', 'ODABRAN ZA PROJEKAT': 'SELECTED FOR THE PROJECT', 'odabran za projekat': 'selected for the project',
    'SCENARIJ': 'SCENARIO', 'PROCJENA': 'ESTIMATE', 'NAPOMENA': 'NOTE', 'procjena': 'estimate',
    'Nije evidentiran finansijski scenario.': 'No financial scenario has been recorded.', 'N/P (isključeno iz obračuna)': 'N/A (excluded from the calculation)', 'N/P': 'N/A',
    'SHA-256 zaključanog snimka:': 'SHA-256 of the locked snapshot:', 'MEVAN  /  Dijagnostika': 'MEVAN  /  Diagnostic',
})

# Tekstovi s brojevima: regularni izraz izvornog teksta i engleski oblik. Uhvaćeni dijelovi ($1…) se
# dodatno prevode ako su sami u rječniku (npr. status). Redoslijed je bitan: prvi pogodak vrijedi.
PATTERNS = [
    (r'^(\d+) potvrđenih / (\d+) primjenjivih kriterija$', '$1 confirmed / $2 applicable criteria'),
    (r'^Indeks (.+)$', 'Index $1'),
    (r'^(\d+)/(\d+) potvrđeno$', '$1/$2 confirmed'),
    (r'^Kriterij (\d+) od (\d+)$', 'Criterion $1 of $2'),
    (r'^(\d+)/(\d+) validiranih · indeks (.+?)\. Izvještaj se može odobriti tek kada su svi primjenjivi kriteriji potvrđeni\.$',
     '$1/$2 validated · index $3. The report can be approved only when all applicable criteria are confirmed.'),
    (r'^(\S+) · (\d+)/61 potvrđenih$', '$1 · $2/61 confirmed'),
    (r'^Potvrđeno (\d+)/(\d+) · Indeks (.+)$', 'Confirmed $1/$2 · Index $3'),
    (r'^Procijenjeno (\d+)/(\d+) · Status: (.+)$', 'Assessed $1/$2 · Status: $3'),
    (r'^Jasna pravila ocjenjivanja za (\S+)$', 'Clear scoring rules for $1'),
    (r'^Potvrđeni izbjegnuti budući troškovi: (.+) KM godišnje \(odvojeno\)\. Nepotvrđeni: (\d+)\. S potencijalnim preklapanjem: (\d+)\.$',
     'Confirmed avoided future costs: $1 KM per year (separate). Unconfirmed: $2. With potential overlap: $3.'),
    (r'^(.+) KM godišnje$', '$1 KM per year'),
    (r'^(.+) KM jednokratno$', '$1 KM one-off'),
    (r'^Aktivno: (.+) · model (.+) · ključ završava na …(.+)$', 'Active: $1 · model $2 · key ends in …$3'),
    (r'^Aktivno: ključ iz postavki servera · model (.+)\. Ključ unesen ovdje ima prednost\.$', 'Active: key from server settings · model $1. A key entered here takes precedence.'),
    (r'^Novi status: (.+)$', 'New status: $1'),
]

# ---- Word izvozi iz preglednika (stranica „Izvještaji” i integrisana analiza)
EN.update({
    'IZVJEŠTAJ O OPERATIVNOJ I POSLOVNOJ ZRELOSTI': 'OPERATIONAL AND BUSINESS MATURITY REPORT', 'Detaljni izvještaj': 'Detailed report', 'Izvršni sažetak': 'Executive summary',
    'METALPRO DEMO – SIMULIRANI PODACI': 'METALPRO DEMO – SIMULATED DATA', 'ZAKLJUČANI NACRT': 'LOCKED DRAFT', 'NEODOBRENI NACRT – NIJE ZA KLIJENTA': 'UNAPPROVED DRAFT – NOT FOR THE CLIENT',
    'Ocjene mjere zrelost procesa, a ne direktno ostvareni poslovni rezultat. Potvrđeni statusi u DEMO podacima ne znače provjeru stvarne kompanije.': 'Scores measure process maturity, not a directly achieved business result. Confirmed statuses in DEMO data do not mean a real company was checked.',
    '01  |  Izvršni pregled': '01  |  Executive overview', 'Pokazatelj': 'Indicator', 'Obuhvat': 'Coverage', 'Status izvještaja': 'Report status',
    'DEMO snimak — simulacija': 'DEMO snapshot — simulation', 'Radni nacrt': 'Working draft', 'Dokazna osnova': 'Evidence basis', 'Isključivo simulirana': 'Simulated only',
    'Prema unesenim dokazima; potrebna stručna provjera': 'Based on entered evidence; expert review required',
    'UPOZORENJE: Dijagnostika nije kompletirana. Indeks se odnosi samo na potvrđene primjenjive kriterije.': 'WARNING: The diagnostic is not complete. The index covers confirmed applicable criteria only.',
    'Pregled pet dimenzija': 'Overview of the five dimensions', 'Dimenzija': 'Dimension', 'Indeks / 100': 'Index / 100', 'Prioriteti za provjeru': 'Priorities for review',
    'Sljedeći kriteriji imaju najniže potvrđene ocjene zrelosti. To su kandidati za analizu, a ne automatski dokazani korijenski uzroci.': 'The following criteria have the lowest confirmed maturity scores. They are candidates for analysis, not automatically proven root causes.',
    'Kriterij': 'Criterion', 'Ocjena': 'Score', 'Pitanje za rukovodstvo': 'Question for management',
    'Nema potvrđenih ocjena na osnovu kojih se može odrediti prioritet.': 'There are no confirmed scores from which a priority can be set.', 'Odluke koje treba pripremiti': 'Decisions to prepare',
    '02  |  Finansijski efekti i ograničenja': '02  |  Financial effects and limitations', 'Stručno potvrđeno u registru': 'Expert-confirmed in the register',
    'Direktne godišnje uštede': 'Direct annual savings', 'Izbjegnuti budući troškovi': 'Avoided future costs', 'Oslobođeni obrtni kapital (jednokratno)': 'Released working capital (one-off)',
    'Nepotvrđene stavke': 'Unconfirmed items', 'Moguća preklapanja': 'Possible overlaps',
    'DEMO SCENARIJ (nije potvrđena korist): godišnji potencijal 52.167 KM i jednokratno oslobađanje obrtnog kapitala 160.000 KM. Kategorije se ne sabiraju bez provjere preklapanja, osnovice i realizacije.': 'DEMO SCENARIO (not a confirmed benefit): annual potential of 52,167 KM and a one-off working capital release of 160,000 KM. Categories are not added up without checking overlaps, baseline and realisation.',
    'Godišnje uštede, izbjegnuti troškovi, dodatna kontribucija i jednokratno oslobađanje gotovine nisu ista finansijska kategorija. Procjena potencijala nije realizovana ušteda.': 'Annual savings, avoided costs, additional contribution and a one-off cash release are not the same financial category. An estimate of potential is not a realised saving.',
    '03  |  Integrisana COO analiza': '03  |  Integrated COO analysis',
    'Integrisana analiza nije unesena ili nije odobrena. Sam indeks zrelosti nije dovoljan za tvrdnje o uzročno-posljedičnim vezama.': 'The integrated analysis has not been entered or approved. The maturity index alone is not enough for claims about cause and effect.',
    'Neodobreno / promijenjeni podaci.': 'Not approved / data changed.', 'DEMO snimak — simulirani podaci': 'DEMO snapshot — simulated data',
    '04  |  Plan prvih 90 dana': '04  |  Plan for the first 90 days', 'Odgovorni': 'Owner', 'Nije uneseno': 'Not entered', 'Nije dodijeljen': 'Not assigned', 'Nije određen': 'Not set', 'Nije definisan': 'Not defined',
    'Nema evidentiranog 90-dnevnog plana za ovaj prikaz. Aktivnosti, odgovorni, rokovi i KPI moraju biti dogovoreni s klijentom.': 'No 90-day plan is recorded for this view. Activities, owners, due dates and KPIs must be agreed with the client.',
    'Nije primjenjivo — obuhvat': 'Not applicable — scope', '05  |  Registar kriterija i dokaza': '05  |  Register of criteria and evidence', 'Polje': 'Field', 'Nalaz / podatak': 'Finding / data',
    'Dijagnostičko pitanje': 'Diagnostic question', 'Potrebni dokaz': 'Required evidence', 'Nedostupno': 'Unavailable', 'Dostavljeni dokaz': 'Evidence provided', 'Nije dostavljen': 'Not provided',
    'Nalaz': 'Finding', 'Nije unesen': 'Not entered', 'Finansijski aspekt': 'Financial aspect', 'Nije procijenjen': 'Not assessed', 'Nije unesena': 'Not entered', 'Nije potvrđeno': 'Not confirmed',
    'Metodologija i ograničenja': 'Methodology and limitations',
    'Skala zrelosti 0–5. N/P se isključuje; kriterij bez potvrđenih dokaza ne dobija automatski nulu. Indeks prikazuje samo potvrđene primjenjive ocjene. Niske ocjene nisu dokaz uzroka bez dodatne analize.': 'Maturity scale 0–5. N/A is excluded; a criterion without confirmed evidence does not automatically get a zero. The index shows confirmed applicable scores only. Low scores are not proof of a cause without further analysis.',
    'Dokument je radni dijagnostički materijal. Finansijski efekti zahtijevaju provjeru osnovice, formule, perioda, preklapanja i odobrenje odgovorne osobe.': 'This document is working diagnostic material. Financial effects require a check of the baseline, formula, period and overlaps, and approval by the responsible person.',
    # integrisana analiza
    'Detaljni dijagnostički izvještaj': 'Detailed diagnostic report', 'Direktorski dijagnostički izvještaj': 'Executive diagnostic report', 'MEVAN 4.0 · RADNI NACRT · NIJE ODOBRENO': 'MEVAN 4.0 · WORKING DRAFT · NOT APPROVED',
    '01  |  Izvršni sažetak': '01  |  Executive summary', 'Dokazi': 'Evidence', 'Nezavisna verifikacija nije izvršena': 'No independent verification has been carried out', 'Nacrt / neodobreno': 'Draft / not approved',
    'Pet dimenzija': 'Five dimensions', 'Procijenjeno / obuhvaćeno': 'Assessed / covered',
    'Ocjene su simulirana samoprocjena; broj procijenjenih kriterija nije broj nezavisno verificiranih dokaza.': 'Scores are a simulated self-assessment; the number of assessed criteria is not the number of independently verified pieces of evidence.',
    '02  |  Sistemski nalazi': '02  |  Systemic findings', '03  |  Direktorske odluke': '03  |  Executive decisions', '02  |  Tri prioritetne direktorske odluke': '02  |  Three priority executive decisions',
    '04  |  KPI registar': '04  |  KPI register', '05  |  Finansijska kontrola': '05  |  Financial control', '03  |  Finansijska kontrola': '03  |  Financial control',
    '06  |  Plan 30/60/90 dana': '06  |  30/60/90-day plan', '04  |  Narednih 30 dana': '04  |  Next 30 days', '07  |  Registar svih kriterija i dokaza': '07  |  Register of all criteria and evidence',
    '08  |  Pitanja za konsultanta': '08  |  Questions for the consultant', '0–30 dana': 'Days 0–30', 'Status: HIPOTEZA': 'Status: HYPOTHESIS',
    'EBITDA i godišnji P&L efekti odvojeni su od jednokratnog oslobađanja obrtnog kapitala. Nema automatski odobrenih efekata.': 'EBITDA and annual P&L effects are kept separate from the one-off working capital release. No effects are approved automatically.',
    'Nezavisno potvrđeni i konsultantski odobreni efekti: 0 KM godišnje; 0 KM jednokratno.': 'Independently confirmed and consultant-approved effects: 0 KM per year; 0 KM one-off.',
    'Hipotetični scenarij': 'Hypothetical scenario', 'Godišnje KM': 'Annual KM', 'Jednokratno KM': 'One-off KM', 'Svi prikazani scenariji su neodobreni i isključeni iz potvrđenih efekata.': 'All scenarios shown are unapproved and excluded from confirmed effects.',
    'Indeks i finansijski iznosi preuzeti su iz determinističkog analitičkog mehanizma. Uzroci su hipoteze. Izvještaj nije validiran niti odobren.': 'The index and financial amounts come from the deterministic analytical mechanism. Causes are hypotheses. The report is not validated or approved.',
    'Kriteriji:': 'Criteria:', 'Mehanizam:': 'Mechanism:', 'Konkurentska hipoteza o uzroku:': 'Competing cause hypothesis:', 'Provjera:': 'Verification:', 'Zašto:': 'Why:', 'Vlasnik:': 'Owner:',
    'Prvih 7 dana:': 'First 7 days:', 'Pilot 30 dana:': '30-day pilot:', 'Uslov / stop:': 'Gate / stop:', 'Kako utvrditi početno stanje:': 'How to establish the baseline:', 'Formula:': 'Formula:',
    'Početna vrijednost:': 'Baseline value:', 'Metod određivanja cilja:': 'Target-setting method:', 'Prag za odluku:': 'Decision threshold:', 'Odgovoran:': 'Responsible:', 'Isporuka:': 'Deliverable:',
    'Dokaz završetka:': 'Evidence of completion:', 'Upozorenje:': 'Warning:', 'Dokaz:': 'Evidence:', 'Nalaz:': 'Finding:', 'Datum:': 'Date:',
})
PATTERNS[:0] = [
    (r'^Datum: (.+?)   \|   Verzija: (.+?)   \|   (.+)$', 'Date: $1   |   Version: $2   |   $3'),
    (r'^(\d+) / (\d+) primjenjivih kriterija$', '$1 / $2 applicable criteria'),
    (r'^(\d+)\. Provjeriti (\S+) – (.+?): (.+)\. Odluka tek nakon provjere dokaza, uzroka, troška i odgovorne osobe\.$',
     '$1. Review $2 – $3: $4. Decide only after checking the evidence, cause, cost and owner.'),
    (r'^Status analize: (.+)$', 'Analysis status: $1'),
]

def lang_of(request):
    value = request.cookies.get(COOKIE, '')
    return value if value in LANGS else DEFAULT


def t(lang, text):
    return EN.get(text, text) if lang == 'en' else text


def client_script(lang):
    """Jezik, rječnik i obrasci za zajedničku skriptu. Na bosanskom se ne šalju."""
    words = json.dumps(EN if lang == 'en' else {}, ensure_ascii=False).replace('</', '<\\/')
    patterns = json.dumps(PATTERNS if lang == 'en' else [], ensure_ascii=False).replace('</', '<\\/')
    catalogue = ''
    if lang == 'en':
        from mevan_criteria_en import CRITERIA_EN
        catalogue = 'window.MV_CRITERIA_EN=' + json.dumps(CRITERIA_EN, ensure_ascii=False).replace('</', '<\\/') + ';'
    return f'<script id="mevan-i18n">window.MV_LANG={json.dumps(lang)};window.MV_I18N={words};window.MV_I18N_PATTERNS={patterns};{catalogue}</script>'
