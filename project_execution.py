"""MEVAN 4.0 project execution foundation. No AI-generated content is auto-approved."""
import hashlib, json, os, re, sqlite3, time, uuid
from datetime import date
from contextlib import contextmanager
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from typing import Literal

router = APIRouter(prefix='/api/v4')

@contextmanager
def db(req):
    # Uses the same configured database as the existing app.
    from server import DB
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.execute('''CREATE TABLE IF NOT EXISTS v4_projects (
      id TEXT PRIMARY KEY, company_id TEXT NOT NULL, diagnostic_id TEXT NOT NULL,
      title TEXT NOT NULL, charter TEXT NOT NULL, status TEXT NOT NULL,
      approved_at INTEGER, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS v4_weekly_reviews (
      id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES v4_projects(id),
      week TEXT NOT NULL, payload TEXT NOT NULL, created_at INTEGER NOT NULL,
      UNIQUE(project_id,week))''')
    c.execute('''CREATE TABLE IF NOT EXISTS v4_financial_models (project_id TEXT PRIMARY KEY REFERENCES v4_projects(id), payload TEXT NOT NULL, updated_at INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS v4_actual_effects (
      id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES v4_projects(id),
      payload TEXT NOT NULL, created_at INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS v4_project_audit (
      id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES v4_projects(id),
      action TEXT NOT NULL, previous_payload TEXT, new_payload TEXT, created_at INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS v4_candidate_drafts (
      company_id TEXT NOT NULL, diagnostic_id TEXT NOT NULL,
      payload TEXT NOT NULL, revision INTEGER NOT NULL, updated_at INTEGER NOT NULL,
      PRIMARY KEY(company_id,diagnostic_id))''')
    try:
        yield c
    finally:
        c.close()

def record_audit(c, pid, action, before, after, now=None):
    """Append an audit entry in the SAME transaction as the business mutation."""
    def serialize(value):
        if value is None: return None
        if isinstance(value,str): return value
        return json.dumps(value,ensure_ascii=False,sort_keys=True)
    c.execute('INSERT INTO v4_project_audit VALUES(?,?,?,?,?,?)',
              (str(uuid.uuid4()),pid,action,serialize(before),serialize(after),now or int(time.time())))

def guard(req, mutation=False):
    from server import logged, same_origin
    if not logged(req):raise HTTPException(401,'Prijava je obavezna')
    if mutation and not same_origin(req):raise HTTPException(403,'Nedozvoljen izvor')

class Charter(BaseModel):
    report_mode: Literal['real','demo'] = 'real'
    problem: str = Field(min_length=10,max_length=4000)
    objective: str = Field(min_length=10,max_length=4000)
    scope: str = Field(min_length=3,max_length=4000)
    methodology: str = Field(min_length=3,max_length=300)
    assumptions: list[str] = Field(default_factory=list,max_length=30)
    required_checks: list[str] = Field(default_factory=list,max_length=30)
    baseline_verified: bool = False
    targets_approved: bool = False
    checks_completed: bool = False
    activities: list[dict] = Field(default_factory=list,max_length=100)
    kpis: list[dict] = Field(default_factory=list,max_length=30)
    financial_effects: list[dict] = Field(default_factory=list,max_length=30)

class ProjectIn(BaseModel):
    company_id: str = Field(min_length=1,max_length=100)
    diagnostic_id: str = Field(min_length=1,max_length=100)
    title: str = Field(min_length=5,max_length=200)
    charter: Charter

class ReviewIn(BaseModel):
    week: str = Field(pattern=r'^\d{4}-W\d{2}$')
    activities: list[dict] = Field(default_factory=list,max_length=100)
    kpi_measurements: list[dict] = Field(default_factory=list,max_length=50)
    blockers: list[str] = Field(default_factory=list,max_length=50)
    decisions: list[str] = Field(default_factory=list,max_length=50)
    note: str = Field(default='',max_length=4000)

    @field_validator('week')
    @classmethod
    def valid_iso_week(cls, value):
        # Week 53 is valid only in some years; 00 and 54+ are never valid.
        year, week = value.split('-W')
        try:
            date.fromisocalendar(int(year), int(week), 1)
        except ValueError as exc:
            raise ValueError('Neispravna ISO sedmica') from exc
        return value

@router.post('/projects',status_code=201)
def create_project(payload:ProjectIn,req:Request):
    guard(req,True)
    now=int(time.time()); pid=str(uuid.uuid4())
    with db(req) as c:
        # One active project per diagnostic; archived projects are allowed.
        active=c.execute("SELECT id FROM v4_projects WHERE company_id=? AND diagnostic_id=? AND status!='closed'",(payload.company_id,payload.diagnostic_id)).fetchone()
        if active:raise HTTPException(409,'Dijagnostika već ima aktivan projektni nacrt')
        c.execute('INSERT INTO v4_projects VALUES(?,?,?,?,?,?,?,?,?)',(pid,payload.company_id,payload.diagnostic_id,payload.title,payload.charter.model_dump_json(),'draft',None,now,now))
        c.execute('INSERT INTO v4_project_audit VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),pid,'created',None,payload.charter.model_dump_json(),now))
        c.commit()
    return {'id':pid,'status':'draft'}


@router.get('/projects/{pid}/audit')
def project_audit(pid:str,req:Request):
    """Immutable history of project creation, charter revisions and approvals."""
    guard(req)
    with db(req) as c:
        if not c.execute('SELECT 1 FROM v4_projects WHERE id=?',(pid,)).fetchone():
            raise HTTPException(404,'Projekat nije pronađen')
        rows=c.execute('SELECT id,action,previous_payload,new_payload,created_at FROM v4_project_audit WHERE project_id=? ORDER BY created_at,rowid',(pid,)).fetchall()
        return {'events':[dict(r) for r in rows]}

@router.get('/projects')
def list_projects(req:Request):
    guard(req)
    with db(req) as c:
        rows=c.execute('SELECT id,company_id,diagnostic_id,title,status,approved_at,created_at,updated_at FROM v4_projects ORDER BY created_at DESC').fetchall()
        return {'projects':[dict(r) for r in rows]}

@router.get('/projects/{pid}')
def get_project(pid:str,req:Request):
    guard(req)
    with db(req) as c:
        row=c.execute('SELECT * FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404)
        data=dict(row);data['charter']=json.loads(data['charter'])
        data['weekly_reviews']=[json.loads(r['payload']) for r in c.execute('SELECT week,payload FROM v4_weekly_reviews WHERE project_id=? ORDER BY week',(pid,))]
        return data

@router.put('/projects/{pid}/charter')
def edit_project(pid:str,payload:Charter,req:Request):
    guard(req,True)
    with db(req) as c:
        row=c.execute('SELECT status,charter FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404)
        if row['status'] not in ('draft','validation'):raise HTTPException(409,'Odobren projekat se ne mijenja bez nove verzije')
        if json.loads(row['charter']).get('report_mode','real')!=payload.report_mode:
            raise HTTPException(409,'Način postojećeg projekta se ne može preimenovati; DEMO ostaje simulacija')
        now=int(time.time()); new_charter=payload.model_dump_json()
        if json.loads(row['charter']) != json.loads(new_charter):
            c.execute('UPDATE v4_projects SET charter=?,updated_at=? WHERE id=?',(new_charter,now,pid))
            c.execute('INSERT INTO v4_project_audit VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),pid,'charter_edited',row['charter'],new_charter,now))
        c.commit()
    return {'ok':True}

@router.post('/projects/{pid}/approve-validation')
def approve_validation(pid:str,req:Request):
    guard(req,True)
    with db(req) as c:
        row=c.execute('SELECT status FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404)
        if row['status']!='draft':raise HTTPException(409,'Neispravan prijelaz statusa')
        now=int(time.time())
        c.execute("UPDATE v4_projects SET status='validation',updated_at=? WHERE id=?",(now,pid))
        c.execute('INSERT INTO v4_project_audit VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),pid,'validation_approved','draft','validation',now))
        c.commit()
    return {'status':'validation'}

@router.post('/projects/{pid}/approve-implementation')
def approve_implementation(pid:str,req:Request):
    guard(req,True)
    with db(req) as c:
        row=c.execute('SELECT status,charter FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404)
        if row['status'] not in ('draft','validation'):raise HTTPException(409,'Neispravan prijelaz statusa')
        ch=json.loads(row['charter'])
        if ch.get('report_mode')=='demo':
            raise HTTPException(409,'DEMO — simulirani podaci: nije dozvoljeno stvarno odobrenje implementacije')
        if not all(ch.get(k) for k in ('baseline_verified','targets_approved','checks_completed')):
            raise HTTPException(409,'Prvo potvrditi početno stanje, ciljeve i obavezne provjere')
        now=int(time.time())
        c.execute("UPDATE v4_projects SET status='implementation',approved_at=?,updated_at=? WHERE id=?",(now,now,pid))
        c.execute('INSERT INTO v4_project_audit VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),pid,'implementation_approved',row['status'],'implementation',now))
        c.commit()
    return {'status':'implementation'}

@router.post('/projects/{pid}/weekly-reviews',status_code=201)
def add_review(pid:str,payload:ReviewIn,req:Request):
    guard(req,True)
    with db(req) as c:
        row=c.execute('SELECT status FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404)
        if row['status']!='implementation':raise HTTPException(409,'Sedmični pregled dozvoljen samo u implementaciji')
        try:
            c.execute('INSERT INTO v4_weekly_reviews VALUES(?,?,?,?,?)',(str(uuid.uuid4()),pid,payload.week,payload.model_dump_json(),int(time.time())))
        except sqlite3.IntegrityError:raise HTTPException(409,'Sedmični pregled već postoji')
        record_audit(c,pid,'weekly_review_created',None,{'week':payload.week,'review':payload.model_dump(mode='json')})
        c.commit()
    return {'ok':True,'week':payload.week}


class CandidateDraftIn(BaseModel):
    company_id: str = Field(min_length=1,max_length=100)
    diagnostic_id: str = Field(min_length=1,max_length=100)
    analysis: dict
    ratings: dict
    expected_revision: int = Field(ge=0)
    version: int = Field(default=1,ge=1,le=1)

def candidate_postgres_url():
    # Separate optional database: existing SQLite diagnostics and projects are untouched.
    url=os.getenv('MEVAN_CANDIDATE_DATABASE_URL','').strip()
    if not url:
        raise HTTPException(503,'Serversko čuvanje ocjena nije konfigurirano')
    if not url.startswith(('postgresql://','postgres://')):
        raise HTTPException(503,'Neispravna konfiguracija baze ocjena')
    return url

@router.get('/candidate-drafts')
def get_candidate_draft(company_id:str,diagnostic_id:str,req:Request):
    guard(req)
    if not (1<=len(company_id)<=100 and 1<=len(diagnostic_id)<=100):
        raise HTTPException(422,'Neispravni identifikatori')
    if not os.getenv('MEVAN_CANDIDATE_DATABASE_URL', '').strip():
        with db(req) as c:
            row = c.execute("SELECT payload, revision, updated_at FROM v4_candidate_drafts WHERE company_id=? AND diagnostic_id=?", (company_id, diagnostic_id)).fetchone()
            if not row:
                raise HTTPException(404, 'Serverski nacrt nije pronađen')
            return {'draft': json.loads(row[0]), 'revision': row[1], 'updated_at': row[2]}
    import psycopg
    with psycopg.connect(candidate_postgres_url(),connect_timeout=8) as c:
        row=c.execute('SELECT payload,revision,updated_at FROM v4_candidate_drafts WHERE company_id=%s AND diagnostic_id=%s',(company_id,diagnostic_id)).fetchone()
        if not row:raise HTTPException(404,'Serverski nacrt nije pronađen')
        return {'draft':row[0] if isinstance(row[0],dict) else json.loads(row[0]),'revision':row[1],'updated_at':row[2]}

@router.put('/candidate-drafts')
def put_candidate_draft(payload:CandidateDraftIn,req:Request):
    guard(req,True)
    from project_candidates import prepare_candidates
    if len(payload.model_dump_json())>1000000:
        raise HTTPException(413,'Nacrt je prevelik')
    candidates=prepare_candidates(payload.analysis)['candidates']
    ids={c['id'] for c in candidates}
    if set(payload.ratings)-ids:
        raise HTTPException(422,'Nepostojeći kandidat u ocjenama')
    from project_planner import FACTORS
    for cid,factors in payload.ratings.items():
        if not isinstance(factors,dict) or set(factors)-set(FACTORS):
            raise HTTPException(422,'Neispravni faktori')
        for item in factors.values():
            if not isinstance(item,dict) or not {'value','rationale','evidence'}<=set(item):
                raise HTTPException(422,'Neispravan zapis ocjene')
            value=item['value']
            if value!='' and (str(value) not in ('0','1','2','3','4','5')):
                raise HTTPException(422,'Ocjena mora biti 0–5')
            if any(not isinstance(item[k],str) or len(item[k])>1500 for k in ('rationale','evidence')):
                raise HTTPException(422,'Tekst ocjene je predug')
    data=payload.model_dump(exclude={'expected_revision'})
    from project_planner import weighted_score
    scores = []
    for candidate in candidates:
        factors = payload.ratings.get(candidate['id'], {})
        if all(factors.get(k, {}).get('value', '') != '' for k in FACTORS):
            scores.append({'id': candidate['id'], 'score': weighted_score({k:int(factors[k]['value']) for k in FACTORS})})
    data['ranking'] = sorted(scores, key=lambda item: (-item['score'], item['id']))
    now=int(time.time())
    if not os.getenv('MEVAN_CANDIDATE_DATABASE_URL', '').strip():
        with db(req) as c:
            encoded = json.dumps(data, ensure_ascii=False)
            if payload.expected_revision == 0:
                cursor = c.execute("INSERT INTO v4_candidate_drafts VALUES(?,?,?,1,?) ON CONFLICT(company_id,diagnostic_id) DO NOTHING", (payload.company_id,payload.diagnostic_id,encoded,now))
            else:
                cursor = c.execute("UPDATE v4_candidate_drafts SET payload=?, revision=revision+1, updated_at=? WHERE company_id=? AND diagnostic_id=? AND revision=?", (encoded,now,payload.company_id,payload.diagnostic_id,payload.expected_revision))
            if cursor.rowcount != 1:
                raise HTTPException(409, 'Serverski nacrt je promijenjen. Ponovo učitajte ocjene.')
            c.commit()
        return {'saved':True,'revision':payload.expected_revision+1,'updated_at':now,'ranking':data['ranking']}
    import psycopg
    from psycopg.types.json import Jsonb
    with psycopg.connect(candidate_postgres_url(),connect_timeout=8) as c:
        # Optimistic concurrency: an update succeeds only at the expected revision.
        if payload.expected_revision==0:
            row=c.execute('''INSERT INTO v4_candidate_drafts(company_id,diagnostic_id,payload,revision,updated_at)
              VALUES(%s,%s,%s,1,%s) ON CONFLICT(company_id,diagnostic_id) DO NOTHING RETURNING revision''',
              (payload.company_id,payload.diagnostic_id,Jsonb(data),now)).fetchone()
        else:
            row=c.execute('''UPDATE v4_candidate_drafts SET payload=%s,revision=revision+1,updated_at=%s
              WHERE company_id=%s AND diagnostic_id=%s AND revision=%s RETURNING revision''',
              (Jsonb(data),now,payload.company_id,payload.diagnostic_id,payload.expected_revision)).fetchone()
        if not row:
            raise HTTPException(409,'Serverski nacrt je promijenjen. Učitajte ga i uporedite prije ponovnog čuvanja.')
    return {'saved':True,'revision':row[0],'updated_at':now,'ranking':data['ranking']}

@router.post('/project-candidates')
def project_candidates(payload:dict,req:Request):
    """Prepare candidate decisions, without inventing quantified impact or auto-approval."""
    guard(req,True)
    from project_candidates import prepare_candidates
    analysis=payload.get('analysis')
    if not isinstance(analysis,dict):raise HTTPException(422,'Nedostaje analiza')
    return prepare_candidates(analysis)


@router.post('/rank-projects')
def rank_projects(payload:dict,req:Request):
    guard(req,True)
    from project_planner import RankRequest,rank
    try:
        p=RankRequest.model_validate(payload)
        return rank(p.analysis,p.ratings)
    except ValueError as e:
        raise HTTPException(422,str(e))

@router.post('/project-draft')
def generate_project_draft(payload:dict,req:Request):
    guard(req,True)
    from project_planner import DraftRequest,draft
    try:
        return draft(DraftRequest.model_validate(payload))
    except ValueError as e:
        raise HTTPException(422,str(e))

@router.post('/project-ai-pack')
def project_ai_pack(payload:dict,req:Request):
    """AI-generated unapproved pack; never persists or activates a project."""
    guard(req,True)
    from project_planner import DraftRequest
    from project_ai_pack import generate
    try:
        return generate(DraftRequest.model_validate(payload))
    except (ValueError,KeyError,TypeError) as e:
        raise HTTPException(422,'AI projektni nacrt nije validan: '+str(e)[:200])
    except RuntimeError as e:
        raise HTTPException(503,str(e))
    except Exception:
        raise HTTPException(502,'AI servis trenutno nije dostupan ili odgovor nije ispravan')


def validated_financial_model(payload:dict):
    """Neispravan ručni unos je greška korisnika (422), ne greška servera (500)."""
    from project_finance import FinancialModel
    from pydantic import ValidationError
    try:
        return FinancialModel.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(422,'Provjerite finansijski model: potrebna su tri scenarija (pesimistični, realni, optimistični) s ispravnim iznosima, izvorima i pretpostavkama.') from exc


@router.post('/financial-scenarios/calculate')
def calculate_financial_scenarios(payload:dict,req:Request):
    """Stateless, deterministic preview. Does not approve or persist any benefit."""
    guard(req,True)
    from project_finance import calculate
    return calculate(validated_financial_model(payload))


@router.get('/projects/{pid}/financial-model')
def get_project_financial_model(pid:str,req:Request):
    guard(req)
    with db(req) as c:
        row=c.execute('SELECT status FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404,'Projekat nije pronađen')
        saved=c.execute('SELECT payload,updated_at FROM v4_financial_models WHERE project_id=?',(pid,)).fetchone()
        if not saved:return {'model':None,'calculation':None,'updated_at':None}
        from project_finance import FinancialModel,calculate
        model=FinancialModel.model_validate_json(saved['payload'])
        return {'model':model.model_dump(mode='json'),'calculation':calculate(model),'updated_at':saved['updated_at']}

@router.put('/projects/{pid}/financial-model')
def save_project_financial_model(pid:str,payload:dict,req:Request):
    guard(req,True)
    from project_finance import calculate
    model=validated_financial_model(payload)
    with db(req) as c:
        row=c.execute('SELECT status FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404,'Projekat nije pronađen')
        if row['status'] not in ('draft','validation'):
            raise HTTPException(409,'Finansijski scenariji odobrenog projekta su zaključani')
        now=int(time.time())
        previous=c.execute('SELECT payload FROM v4_financial_models WHERE project_id=?',(pid,)).fetchone()
        old=json.loads(previous['payload']) if previous else None
        new=model.model_dump(mode='json')
        if old != new:
            c.execute('INSERT INTO v4_financial_models(project_id,payload,updated_at) VALUES(?,?,?) ON CONFLICT(project_id) DO UPDATE SET payload=excluded.payload,updated_at=excluded.updated_at',(pid,model.model_dump_json(),now))
            record_audit(c,pid,'financial_model_updated' if previous else 'financial_model_created',old,new,now)
        c.commit()
    return {'saved':True,'calculation':calculate(model)}


@router.get('/projects/{pid}/actual-effects')
def get_actual_effects(pid:str,req:Request):
    guard(req)
    from project_actuals import summarize
    with db(req) as c:
        if not c.execute('SELECT 1 FROM v4_projects WHERE id=?',(pid,)).fetchone():raise HTTPException(404)
        rows=c.execute('SELECT id,payload,created_at FROM v4_actual_effects WHERE project_id=? ORDER BY created_at,id',(pid,)).fetchall()
        entries=[dict(id=r['id'],created_at=r['created_at'],**json.loads(r['payload'])) for r in rows]
    return {'entries':entries,'summary':summarize(entries)}

@router.post('/projects/{pid}/actual-effects',status_code=201)
def add_actual_effect(pid:str,payload:dict,req:Request):
    guard(req,True)
    from project_actuals import ActualIn, canonical_effect
    from pydantic import ValidationError
    try:
        effect=ActualIn.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(422,'Provjerite period, iznos, dokaz, obračun i vlasnika finansijskog efekta.') from exc
    canonical = canonical_effect(effect)
    key = req.headers.get('Idempotency-Key')
    if key is not None and not re.fullmatch(r'[A-Za-z0-9._:-]{1,128}', key):
        raise HTTPException(422,'Oznaka događaja mora imati 1–128 slova bez dijakritike, cifara ili znakova . _ : -')
    # Explicit event IDs permit genuinely distinct events with identical values.
    # Older callers without a key get exact-content retry protection as well.
    identity = 'event:' + key if key is not None else 'payload:' + hashlib.sha256(canonical.encode()).hexdigest()
    eid = str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(['mevan-actual-v1', pid, identity])))
    with db(req) as c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT status FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404)
        previous=c.execute('SELECT payload FROM v4_actual_effects WHERE id=? AND project_id=?',(eid,pid)).fetchone()
        if previous:
            if canonical_effect(ActualIn.model_validate_json(previous['payload'])) != canonical:
                raise HTTPException(409,'Oznaka događaja je već korištena za drugi sadržaj. Ponovite izvorni zahtjev ili koristite novu oznaku za zaseban događaj.')
            return {'id':eid,'status':'consultant_confirmed' if effect.consultant_confirmed else 'pending',
                    'independently_verified':False,'replayed':True}
        if row['status']!='implementation':raise HTTPException(409,'Efekti se evidentiraju samo tokom implementacije')
        now=int(time.time())
        c.execute('INSERT INTO v4_actual_effects VALUES(?,?,?,?)',(eid,pid,effect.model_dump_json(),now))
        record_audit(c,pid,'actual_effect_recorded',None,{'effect_id':eid,'effect':effect.model_dump(mode='json')},now)
        c.commit()
    return {'id':eid,'status':'consultant_confirmed' if effect.consultant_confirmed else 'pending','independently_verified':False,'replayed':False}


@router.get('/projects/{pid}/report/{fmt}')
def project_report(pid:str,fmt:str,req:Request):
    """Authenticated, read-only export. No status or evidence is modified."""
    guard(req)
    if fmt not in ('docx','pdf'):raise HTTPException(404,'Nepodržan format')
    with db(req) as c:
        c.execute('BEGIN')
        row=c.execute('SELECT * FROM v4_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise HTTPException(404,'Projekat nije pronađen')
        data=dict(row);data['charter']=json.loads(data['charter'])
        data['reviews']=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM v4_weekly_reviews WHERE project_id=? ORDER BY week',(pid,))]
        fin=c.execute('SELECT payload FROM v4_financial_models WHERE project_id=?',(pid,)).fetchone()
        data['finance']=json.loads(fin['payload']) if fin else None
        data['effects']=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM v4_actual_effects WHERE project_id=? ORDER BY created_at,id',(pid,))]
    from project_reports import export_docx,export_pdf
    content=export_docx(data) if fmt=='docx' else export_pdf(data)
    media='application/vnd.openxmlformats-officedocument.wordprocessingml.document' if fmt=='docx' else 'application/pdf'
    return Response(content,media_type=media,headers={'Content-Disposition':f'attachment; filename="MEVAN_project_{pid[:8]}.{fmt}"','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})


@router.get('/dashboard')
def project_dashboard(req:Request):
    """Read-only portfolio snapshot; never sums incomparable financial periods."""
    guard(req)
    from datetime import date
    today=date.today().isoformat()
    with db(req) as c:
        rows=c.execute('SELECT id,company_id,diagnostic_id,title,status,created_at,updated_at,charter FROM v4_projects ORDER BY updated_at DESC').fetchall()
        projects=[]
        for r in rows:
            charter=json.loads(r['charter'])
            activities=charter.get('activities') or []
            overdue=[]
            for a in activities:
                if not isinstance(a,dict):continue
                due=a.get('due_date') or a.get('deadline') or ''
                if isinstance(due,str) and len(due)==10 and due[4:5]=='-' and due[7:8]=='-' and due<today:
                    overdue.append({'title':str(a.get('title') or a.get('name') or 'Aktivnost'),'due_date':due})
            last=c.execute('SELECT week,payload FROM v4_weekly_reviews WHERE project_id=? ORDER BY week DESC LIMIT 1',(r['id'],)).fetchone()
            reviews=c.execute('SELECT COUNT(*) FROM v4_weekly_reviews WHERE project_id=?',(r['id'],)).fetchone()[0]
            actuals=c.execute('SELECT payload FROM v4_actual_effects WHERE project_id=?',(r['id'],)).fetchall()
            confirmed=sum(1 for x in actuals if json.loads(x['payload']).get('consultant_confirmed'))
            finance=c.execute('SELECT 1 FROM v4_financial_models WHERE project_id=?',(r['id'],)).fetchone() is not None
            projects.append({'id':r['id'],'company_id':r['company_id'],'diagnostic_id':r['diagnostic_id'],'title':r['title'],'status':r['status'],'updated_at':r['updated_at'],'activities_count':len(activities),'kpis_count':len(charter.get('kpis') or []),'overdue_activities':overdue,'weekly_reviews_count':reviews,'last_week':last['week'] if last else None,'last_kpi_measurements_count':len(json.loads(last['payload']).get('kpi_measurements') or []) if last else 0,'financial_model_present':finance,'actual_entries_count':len(actuals),'consultant_confirmed_entries_count':confirmed,'independently_verified_entries_count':0})
    statuses={}
    for item in projects:statuses[item['status']]=statuses.get(item['status'],0)+1
    return {'projects':projects,'summary':{'companies':len({p['company_id'] for p in projects}),'projects':len(projects),'by_status':statuses,'projects_with_overdue_activities':sum(bool(p['overdue_activities']) for p in projects),'projects_with_financial_model':sum(p['financial_model_present'] for p in projects)},'disclaimer':'Rokovi su iz projektnog nacrta i ne uzimaju u obzir završetak aktivnosti. Iznosi različitih perioda nisu sabrani. Konsultantski potvrđeni efekti nisu nezavisno verificirani.'}
