> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: sva SQLite šema, JSON payloadi, integracije i funkcije; PG nepoznanice.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — baza i arhitektura

## Komponente i tok podataka

Preglednik (HTML/JS + localStorage/sessionStorage) → FastAPI server → SQLite datoteka MEVAN_DB. Opcionalno serverski urllib poziv OpenAI chat-completions. Samo kandidat nacrti mogu koristiti psycopg PostgreSQL kada je MEVAN_CANDIDATE_DATABASE_URL neprazan. Ne postoji Supabase/Cloudflare D1 baza, Redis, queue, ORM, mikroservis ili poseban auth servis.

`server.py:12` bira DB, `server.py:20` pravi app bez javne OpenAPI dokumentacije. `project_execution.py:12` otvara istu DB i uključuje foreign_keys=ON za projektne konekcije. `server.py:616` mounta TEST router također na istu DB putanju; „TEST” znači odvojene tabele, **ne automatski drugi fajl ili tenant izolaciju**. Module docstring „not wired” nije mjerodavan prema stvarnoj integraciji.

Glavni workspace je singleton JSON, TEST workspace drugi singleton s integer revizijom, a projekti su odvojeni relacijski redovi s JSON payloadima. Promjene ova dva workspacea nisu jedna atomska transakcija. Glavni UI nakon loada preuzima samo pregledana polja iz TEST stanja kada se source signature podudara; to nije opći serverski merge. Projects UI se oslanja na company_id/diagnostic_id, bez FK prema JSON kompaniji.

## Izvlačenje stvarne SQLite šeme

Nova privremena baza inicijalizovana je postojećim server.conn, project_execution.db, init_test_store i init_approval_store; svih 10 aplikacijskih tabela imalo je 0 redova. sqlite_sequence je interna tabela SQLite-a. Pročitani su sqlite_master CREATE i PRAGMA table_info/index_list/index_info/foreign_key_list; nije čitana stvarna baza. `notnull` je doslovna PRAGMA vrijednost; `PK=1/2` označava poziciju u ključu, ne boolean. SQLite TEXT PRIMARY KEY u rowid tabeli može imati notnull=0; nema izmišljene implicitne NOT NULL garancije. INTEGER PRIMARY KEY je alias rowid. Unikatni autoindeksi se navode čak i kada ih kod eksplicitno ne imenuje.

### Tabela `audit`

```sql
CREATE TABLE audit (id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER NOT NULL, event TEXT NOT NULL, details TEXT NOT NULL)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | INTEGER | 0 | nema eksplicitnog defaulta | 1 |
| ts | INTEGER | 1 | nema eksplicitnog defaulta | 0 |
| event | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| details | TEXT | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: nema zasebno evidentiranih indeksa.

Izvor inicijalizacije: `project_execution.py:31`, `server.py:58`


### Tabela `diagnostic_approvals_test`

```sql
CREATE TABLE diagnostic_approvals_test (
        approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_revision INTEGER NOT NULL,
        snapshot_json TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        reviewer_id TEXT NOT NULL,
        approved_at INTEGER NOT NULL
    )
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| approval_id | INTEGER | 0 | nema eksplicitnog defaulta | 1 |
| workspace_revision | INTEGER | 1 | nema eksplicitnog defaulta | 0 |
| snapshot_json | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| sha 256 | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| reviewer_id | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| approved_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: nema zasebno evidentiranih indeksa.

Izvor inicijalizacije: `mevan_test_approval.py:21`


### Tabela `sqlite_sequence`

```sql
CREATE TABLE sqlite_sequence(name,seq)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| name |  | 0 | nema eksplicitnog defaulta | 0 |
| seq |  | 0 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: nema zasebno evidentiranih indeksa.

Izvor inicijalizacije: 


### Tabela `v4_actual_effects`

```sql
CREATE TABLE v4_actual_effects (
      id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES v4_projects(id),
      payload TEXT NOT NULL, created_at INTEGER NOT NULL)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | TEXT | 0 | nema eksplicitnog defaulta | 1 |
| project_id | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| payload | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| created_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: `[[0, 0, "v4_projects", "project_id", "id", "NO ACTION", "NO ACTION", "NONE"]]`

Indeksi: `[{"info": [0, "sqlite_autoindex_v4_actual_effects_1", 1, "pk", 0], "columns": [[0, 0, "id"]]}]`

Izvor inicijalizacije: `project_execution.py:28`


### Tabela `v4_candidate_drafts`

```sql
CREATE TABLE v4_candidate_drafts (
      company_id TEXT NOT NULL, diagnostic_id TEXT NOT NULL,
      payload TEXT NOT NULL, revision INTEGER NOT NULL, updated_at INTEGER NOT NULL,
      PRIMARY KEY(company_id,diagnostic_id))
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| company_id | TEXT | 1 | nema eksplicitnog defaulta | 1 |
| diagnostic_id | TEXT | 1 | nema eksplicitnog defaulta | 2 |
| payload | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| revision | INTEGER | 1 | nema eksplicitnog defaulta | 0 |
| updated_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: `[{"info": [0, "sqlite_autoindex_v4_candidate_drafts_1", 1, "pk", 0], "columns": [[0, 0, "company_id"], [1, 1, "diagnostic_id"]]}]`

Izvor inicijalizacije: `project_execution.py:34`


### Tabela `v4_financial_models`

```sql
CREATE TABLE v4_financial_models (project_id TEXT PRIMARY KEY REFERENCES v4_projects(id), payload TEXT NOT NULL, updated_at INTEGER NOT NULL)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| project_id | TEXT | 0 | nema eksplicitnog defaulta | 1 |
| payload | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| updated_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: `[[0, 0, "v4_projects", "project_id", "id", "NO ACTION", "NO ACTION", "NONE"]]`

Indeksi: `[{"info": [0, "sqlite_autoindex_v4_financial_models_1", 1, "pk", 0], "columns": [[0, 0, "project_id"]]}]`

Izvor inicijalizacije: `project_execution.py:27`


### Tabela `v4_project_audit`

```sql
CREATE TABLE v4_project_audit (
      id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES v4_projects(id),
      action TEXT NOT NULL, previous_payload TEXT, new_payload TEXT, created_at INTEGER NOT NULL)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | TEXT | 0 | nema eksplicitnog defaulta | 1 |
| project_id | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| action | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| previous_payload | TEXT | 0 | nema eksplicitnog defaulta | 0 |
| new_payload | TEXT | 0 | nema eksplicitnog defaulta | 0 |
| created_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: `[[0, 0, "v4_projects", "project_id", "id", "NO ACTION", "NO ACTION", "NONE"]]`

Indeksi: `[{"info": [0, "sqlite_autoindex_v4_project_audit_1", 1, "pk", 0], "columns": [[0, 0, "id"]]}]`

Izvor inicijalizacije: `project_execution.py:31`


### Tabela `v4_projects`

```sql
CREATE TABLE v4_projects (
      id TEXT PRIMARY KEY, company_id TEXT NOT NULL, diagnostic_id TEXT NOT NULL,
      title TEXT NOT NULL, charter TEXT NOT NULL, status TEXT NOT NULL,
      approved_at INTEGER, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | TEXT | 0 | nema eksplicitnog defaulta | 1 |
| company_id | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| diagnostic_id | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| title | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| charter | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| status | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| approved_at | INTEGER | 0 | nema eksplicitnog defaulta | 0 |
| created_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |
| updated_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: `[{"info": [0, "sqlite_autoindex_v4_projects_1", 1, "pk", 0], "columns": [[0, 0, "id"]]}]`

Izvor inicijalizacije: `project_execution.py:19`, `project_execution.py:23`, `project_execution.py:27`, `project_execution.py:28`, `project_execution.py:31`


### Tabela `v4_weekly_reviews`

```sql
CREATE TABLE v4_weekly_reviews (
      id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES v4_projects(id),
      week TEXT NOT NULL, payload TEXT NOT NULL, created_at INTEGER NOT NULL,
      UNIQUE(project_id,week))
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | TEXT | 0 | nema eksplicitnog defaulta | 1 |
| project_id | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| week | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| payload | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| created_at | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: `[[0, 0, "v4_projects", "project_id", "id", "NO ACTION", "NO ACTION", "NONE"]]`

Indeksi: `[{"info": [0, "sqlite_autoindex_v4_weekly_reviews_2", 1, "u", 0], "columns": [[0, 1, "project_id"], [1, 2, "week"]]}, {"info": [1, "sqlite_autoindex_v4_weekly_reviews_1", 1, "pk", 0], "columns": [[0, 0, "id"]]}]`

Izvor inicijalizacije: `project_execution.py:23`


### Tabela `workspace`

```sql
CREATE TABLE workspace (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL, updated INTEGER NOT NULL)
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | INTEGER | 0 | nema eksplicitnog defaulta | 1 |
| payload | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| updated | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: nema zasebno evidentiranih indeksa.

Izvor inicijalizacije: `mevan_sync_guard.py:52`, `mevan_test_approval.py:21`, `server.py:57`


### Tabela `workspace_test_v2`

```sql
CREATE TABLE workspace_test_v2 (
        id INTEGER PRIMARY KEY CHECK (id=1),
        payload TEXT NOT NULL,
        revision INTEGER NOT NULL CHECK (revision >= 1),
        updated INTEGER NOT NULL
    )
```

| Kolona | Stvarni tip | NOT NULL (PRAGMA) | Default | PK pozicija |
| --- | --- | --- | --- | --- |
| id | INTEGER | 0 | nema eksplicitnog defaulta | 1 |
| payload | TEXT | 1 | nema eksplicitnog defaulta | 0 |
| revision | INTEGER | 1 | nema eksplicitnog defaulta | 0 |
| updated | INTEGER | 1 | nema eksplicitnog defaulta | 0 |

Strani ključevi: nema deklarisanih FK.

Indeksi: nema zasebno evidentiranih indeksa.

Izvor inicijalizacije: `mevan_sync_guard.py:52`

## Relacije, integritet i transakcije

v 4_weekly_reviews, v 4_financial_models, v 4_actual_effects i v 4_project_audit imaju project_id→v 4_projects.id, bez ON DELETE CASCADE. Foreign key enforcement je uključen na projektnoj konekciji, nije univerzalno uključen na svakoj SQLite konekciji drugih helpera. company_id/diagnostic_id su tekst, bez FK u kompanijsku JSON strukturu; kandidat nacrt ima kompozitni PK(company_id, diagnostic_id). Jedan aktivni projekat provjerava handler SELECT-om, ne SQL unique uslovom. Sedmica ima UNIQUE(project_id, week). Ne postoji poslovni unique constraint na effect payload; stabilni UUIDv5+PK štiti nove identične retry upise. Nema delete API-ja i automatskog spajanja starih zapisa.

Legacy workspace store i actual-effect koriste BEGIN IMMEDIATE; TEST save/approval također; kandidat CAS koristi uslov revision pri UPDATE ili ON CONFLICT DO NOTHING pri prvom INSERT-u. Projektni izvještaj počinje BEGIN i čita konzistentno iz jedne konekcije. db context zatvara konekciju; poslovni mutatori eksplicitno commitaju, exception prije commita ne ostavlja djelimičan upis na zatvaranju. Ne treba tvrditi da svaki drugi projektni statusni mutator ima jednaku konkurentnu zaštitu kao idempotentni effect.

Workspace legacy version je SHA256 tačno sačuvanog JSON stringa; semantički isti drugačije serijalizovan JSON može imati drugi hash. TEST revision je cijeli broj koji raste; restore stvara novu radnu reviziju. Kandidati zasebno imaju revision i version=1 modela. approved snapshot nije pointer na promjenjiv workspace: čuva cijeli JSON i odabrane indekse/diagnostic_id.

## JSON strukture, snapshoti i kompatibilnost

- workspace.payload: `{schema,companies,activeCompanyId,activeDiagnosticId}`; companies[].company je profil, diagnostics[] sadrži assess/plan/approved/review/effects/v2/v3 i nova reviewed polja. Legacy validacija je površinska.
- workspace_test_v 2.payload: isti oblik, plus quality_records, risk_reviews, consultant_review, guided, report_mode. Guided source_assess_signature je JSON string za detekciju promjene, **nije kriptografski potpis**. current_stage jedan od interview/documents/visit/evidence/priorities/project/plan; owner/start_date/kpi/project_id/selected_candidate su tekstualni do 4000. Collection bilješke interview/documents/visit do 10000 znakova. Nema upload bajtova.
- diagnostic_approvals_test.snapshot_json: format mevan-bound-approval-v1 ili -v2; workspace; company_index/diagnostic_index; diagnostic_id; quality_gate. V2 dodaje report_mode i report_model `{version:2,result:<zamrznuti analyze rezultat>}`. hash kanonski sortiran ensure_ascii=false, separators(',',':'), allow_nan=false. Režim se validira prema odabranoj dijagnostici. Metadata reviewer/time/revision u zasebnim kolonama nisu svi dio istog JSON digest sadržaja; ne nazivati ovo vanjskim digitalnim potpisom.
- Charter JSON: report_mode + problem/objective/scope/methodology, assumptions, required_checks, tri bool potvrde, activities/kpis/financial_effects. List dict strukture omogućuju stari/new naziv ključeva; izvještaj i dashboard koriste određene fallbackove. Guided datum due_date i UI deadline nisu potpuno ujednačena šema.
- v 4_candidate_drafts.payload: company_id/diagnostic_id/analysis/ratings/version i serverski ranking; expected_revision nije dio sačuvanog payload-a. Ratings UI koristi `{value,rationale,evidence}` dok rank endpoint koristi `{candidate_id,ratings:{factor:{value,rationale,evidence_ids}}}`; frontend vrši konverziju.
- v 4_financial_models.payload: tri Scenario i Benefit procjene, Decimal iznosi serijalizovani Pydantic JSON-om. Calculation se ne čuva kao nezavisna istina nego ponovo računa.
- v 4_actual_effects.payload: ActualIn bez proizvoljnog klijentskog ID-ja; iznos i tekst canonical služe retry identitetu. Audit previous_payload/new_payload su tekstualni JSON ili stari status stringovi, nisu svi uniformni objekti.

## Opcionalni PostgreSQL — stvarni i nedostajući dijelovi

`project_execution.py:205` zahtijeva URLpostgresql:// ili postgres:// i timeout 8 s. GET/PUT kandidat nacrta koriste %s parametre, Jsonb za payload, RETURNING revision i transakciju psycopg contexta. SQLite koristi ? parametre, payload TEXT, cursor.rowcount i eksplicitni commit. PG payload se čita kao dict ili json.loads; CAS logika je ista po namjeri. Udaljeni PG nije testiran.

U kodu/repozitoriju **nema PG CREATE TABLE/migracije**. Zato stvarni PG tipovi, DEFAULT/NULLability/PK/unique/check/indeksi, RLS i aktivna šema nisu potvrđeni. Upiti očekuju v 4_candidate_drafts(company_id, diagnostic_id, payload, revision, updated_at) i unique konfliktni ključ(company_id, diagnostic_id); to je očekivanje aplikacije, ne dokaz izvršenog DDL-a. Bez pripreme tabela PG put može pasti; ne izmišljati JSONB/BIGINT definiciju kao postojeće stanje. Sve ostalo — workspace, projekti, audit, efekti — ostaje SQLite čak i kada je PG za kandidate aktivan.

## Backup obuhvat

1. `/api/backup`: JSON mevan-backup-v1 samo legacy workspace; ne audit, ne projekti, ne TEST approvals, ne datoteke.
2. `mevan_test_backup.py`: payload/hash mevan-test-snapshot-v1 samo revizionisani TEST workspace; guarded restore upisuje novu radnu reviziju. Nema javnog mountanog snapshot export/restore endpointa u trenutnom TEST routeru.
3. `backup_restore.py`: konzistentan SQLite backup API i integrity_check, uključuje sve tabele iste SQLite datoteke i audit redove, WAL promjene; restore samo na novu putanju. Ne uključuje zaseban PG ili vanjske priloge. Nema šifrovanja/offsite/schedule automatike.

Puni SQLite restore u prethodnim sintetičkim testovima ne poništava raniji nalaz da TEST JSON backup nije cijela baza. To su različiti formati i obuhvati. Generisanje PDF/DOCX nije automatsko arhiviranje bajtova izvještaja u bazi. Prilozi su reference, ne implementirano skladište. Prenos source/bundle u ovom zadatku nije migracija podataka.

## Inventar serverskih funkcija i servisa

Tabela uključuje sve netestne Python funkcije (i offline QA/CLI/browser pomoćnike, jasno po datoteci); glavni API je zasebno potpuno opisan u [funkcionalnoj specifikaciji](FUNCTIONAL_SPECIFICATION.md). Detaljna AST lista uključujući testne helper funkcije je u `inventari/funkcije.json`. Nema pretpostavljenih pozadinskih jobova; pozivi se izvršavaju u handleru ili eksplicitnom CLI procesu.

| Izvor | Funkcija | Potpis / uloga iz koda |
| --- | --- | --- |
| approved_reports.py:33 | validate_review | diagnostic, *, for_approval=False — Technical completeness only, never a professional assessment of quality.<br><br>Stricter rules apply to NEW approvals, not historical snapshot downloads. |
| approved_reports.py:58 | report_sections | db, approval_id, view |
| approved_reports.py:137 | radar_png | result — Nepoznata ili prazna oblast se ne pretvara u nulu radi crtanja radara. |
| approved_reports.py:155 | render | db, approval_id, view, fmt |
| approved_reports.py:146 | points | scale |
| approved_reports.py:187 | label_page | canvas, doc |
| backup_restore.py:11 | integrity_check | path: Path |
| backup_restore.py:23 | backup | source: Path, destination: Path |
| backup_restore.py:43 | restore | source: Path, destination: Path — Restore only to a NEW path; stop the app before switching DB paths. |
| data_quality_gate.py:8 | valid_na_reason | value |
| data_quality_gate.py:16 | check_record | record, policy_version=2 |
| data_quality_gate.py:56 | check_batch | records, policy_version=2 |
| diagnostic_engine.py:15 | num | value |
| diagnostic_engine.py:21 | analyze | payload |
| http_release_smoke.py:13 | main |  |
| http_release_smoke.py:11 | redirect_request | self, req, fp, code, msg, headers, newurl |
| http_release_smoke.py:23 | get | path |
| metalpro_demo.py:10 | diagnostic |  |
| metalpro_demo.py:23 | analysis |  |
| metalpro_demo.py:26 | candidate_ratings | analysis_data |
| metalpro_demo.py:32 | project_draft |  |
| metalpro_demo.py:35 | finance_model |  |
| metalpro_demo.py:39 | demo_summary |  |
| mevan_report_gate.py:10 | evaluate_report_gate | records, approved_revision, report_revision, reviewer_id, risk_reviews=None, finance_claims=None, *, mode='real', policy_version=2 |
| mevan_report_model.py:7 | has_simulated_inputs | company, diagnostic |
| mevan_report_model.py:15 | freeze_model | diagnostic |
| mevan_sync_guard.py:19 | validate_workspace | workspace: Any |
| mevan_sync_guard.py:50 | init_test_store | db: sqlite3.Connection — Create separate TEST table; does not modify legacy workspace. |
| mevan_sync_guard.py:61 | read_test_workspace | db: sqlite3.Connection |
| mevan_sync_guard.py:72 | save_test_workspace | db: sqlite3.Connection, workspace: dict, expected_revision: int — Atomic compare-and-swap; raises conflict instead of overwriting. |
| mevan_test_approval.py:17 | _canonical | value |
| mevan_test_approval.py:20 | init_approval_store | db: sqlite3.Connection |
| mevan_test_approval.py:31 | approve_workspace | db: sqlite3.Connection, expected_revision: int, reviewer_id: str, company_index: int, diagnostic_index: int |
| mevan_test_approval.py:90 | read_approval | db: sqlite3.Connection, approval_id: int |
| mevan_test_backup.py:12 | canonical | data |
| mevan_test_backup.py:16 | export_snapshot | db: sqlite3.Connection |
| mevan_test_backup.py:24 | verify_snapshot | snapshot: dict |
| mevan_test_backup.py:38 | restore_snapshot | db: sqlite3.Connection, snapshot: dict, expected_revision: int, confirm: str — Explicit TEST restore; refuses stale revision and corrupt snapshot.<br><br>Callers must export and securely retain a pre-restore snapshot before use. |
| mevan_test_report_manifest.py:16 | prepare_report_manifest | db, approval_id: int, company_index: int, diagnostic_index: int |
| mevan_test_report_manifest.py:11 | __init__ | self, result |
| mevan_test_workspace_api.py:31 | create_test_router | db_path: str, authorize: Callable[[Request], bool], verify_write_origin: Callable[[Request], bool], reviewer_id: str='' — Fail closed: integration MUST provide explicit security callbacks. |
| mevan_test_workspace_api.py:41 | require_auth | request: Request |
| mevan_test_workspace_api.py:50 | connect |  |
| mevan_test_workspace_api.py:54 | get_test_workspace |  |
| mevan_test_workspace_api.py:60 | put_test_workspace | body: SaveRequest, request: Request |
| mevan_test_workspace_api.py:83 | approve | body: ApprovalRequest, request: Request |
| mevan_test_workspace_api.py:107 | approvals |  |
| mevan_test_workspace_api.py:115 | download | approval_id: int, view: Literal['executive', 'detailed'], fmt: Literal['pdf', 'docx'] |
| project_actuals.py:25 | canonical_effect | effect: ActualIn — Stable request identity; numeric JSON spellings are the same amount. |
| project_actuals.py:33 | summarize | entries |
| project_actuals.py:19 | safe | self |
| project_ai_pack.py:36 | assemble | base, plan: AIPlan — AI cannot override approval flags or insert quantified benefits. |
| project_ai_pack.py:56 | generate | payload: DraftRequest, transport=None |
| project_candidates.py:8 | prepare_candidates | analysis: dict |
| project_execution.py:13 | db | req |
| project_execution.py:43 | record_audit | c, pid, action, before, after, now=None — Append an audit entry in the SAME transaction as the business mutation. |
| project_execution.py:52 | guard | req, mutation=False |
| project_execution.py:98 | create_project | payload: ProjectIn, req: Request |
| project_execution.py:112 | project_audit | pid: str, req: Request — Immutable history of project creation, charter revisions and approvals. |
| project_execution.py:122 | list_projects | req: Request |
| project_execution.py:129 | get_project | pid: str, req: Request |
| project_execution.py:139 | edit_project | pid: str, payload: Charter, req: Request |
| project_execution.py:155 | approve_validation | pid: str, req: Request |
| project_execution.py:168 | approve_implementation | pid: str, req: Request |
| project_execution.py:186 | add_review | pid: str, payload: ReviewIn, req: Request |
| project_execution.py:208 | candidate_postgres_url |  |
| project_execution.py:218 | get_candidate_draft | company_id: str, diagnostic_id: str, req: Request |
| project_execution.py:235 | put_candidate_draft | payload: CandidateDraftIn, req: Request |
| project_execution.py:293 | project_candidates | payload: dict, req: Request — Prepare candidate decisions, without inventing quantified impact or auto-approval. |
| project_execution.py:303 | rank_projects | payload: dict, req: Request |
| project_execution.py:313 | generate_project_draft | payload: dict, req: Request |
| project_execution.py:322 | project_ai_pack | payload: dict, req: Request — AI-generated unapproved pack; never persists or activates a project. |
| project_execution.py:338 | calculate_financial_scenarios | payload: dict, req: Request — Stateless, deterministic preview. Does not approve or persist any benefit. |
| project_execution.py:346 | get_project_financial_model | pid: str, req: Request |
| project_execution.py:358 | save_project_financial_model | pid: str, payload: dict, req: Request |
| project_execution.py:379 | get_actual_effects | pid: str, req: Request |
| project_execution.py:389 | add_actual_effect | pid: str, payload: dict, req: Request |
| project_execution.py:424 | project_report | pid: str, fmt: str, req: Request — Authenticated, read-only export. No status or evidence is modified. |
| project_execution.py:444 | project_dashboard | req: Request — Read-only portfolio snapshot; never sums incomparable financial periods. |
| project_execution.py:45 | serialize | value |
| project_execution.py:88 | valid_iso_week | cls, value |
| project_finance.py:39 | money | d |
| project_finance.py:42 | calculate | model: FinancialModel |
| project_finance.py:15 | no_false_confirmation | self |
| project_finance.py:30 | check_names | self |
| project_planner.py:30 | weighted_score | values |
| project_planner.py:34 | rank | analysis, ratings |
| project_planner.py:58 | draft | payload: DraftRequest |
| project_reports.py:24 | clean | v |
| project_reports.py:29 | build_sections | data |
| project_reports.py:50 | export_docx | data |
| project_reports.py:62 | export_pdf | data |
| project_reports.py:31 | add | title, items |
| project_reports.py:70 | footer | canvas, doc |
| release_preflight.py:10 | check_bundle |  |
| release_preflight.py:28 | check_runtime |  |
| remote_acceptance.py:17 | validate_target | url |
| remote_acceptance.py:25 | check | base, opener=None |
| remote_acceptance.py:55 | main |  |
| remote_acceptance.py:14 | redirect_request | self, request, fp, code, msg, headers, newurl |
| server.py:22 | security_headers | request, call_next |
| server.py:37 | same_origin | req |
| server.py:54 | conn |  |
| server.py:67 | sign | payload |
| server.py:71 | logged | req |
| server.py:81 | login_csrf_token |  |
| server.py:88 | valid_login_csrf | token |
| server.py:97 | login_page |  |
| server.py:101 | login | req: Request |
| server.py:126 | logout | req: Request |
| server.py:133 | home | req: Request |
| server.py:139 | load | req: Request |
| server.py:147 | store | req: Request |
| server.py:173 | data_quality_check | req: Request — Test-only, read-only validation; does not mutate assessments or reports. |
| server.py:187 | backup | req: Request — Administrator-triggered JSON export; must be stored securely by operator. |
| server.py:198 | audit | req: Request |
| server.py:204 | restore | req: Request |
| server.py:224 | diagnostic_v 2 | req: Request — Deterministic, evidence-aware cross-dimension draft. No external AI call. |
| server.py:237 | health |  |
| server.py:241 | ai_draft | req: Request — Optional real AI. Only a draft; approval remains a separate human action. |
| server.py:311 | ai_integrated | req: Request — Integrated cross-functional AI draft; never an approved professional finding. |
| server.py:382 | decision_intelligence | req: Request — v2.3: auditable, unapproved decision recommendations grounded in rule output. |
| server.py:447 | mevan_v 3_analyze | req: Request — One evidence-aware analysis; two report views share one canonical fact base.<br><br>This endpoint is a v3 foundation, NOT final report generation or approval. |
| server.py:604 | project_ui | req: Request |
| server.py:611 | dashboard_ui | req: Request |
| server.py:621 | diagnostic_review | req: Request |
