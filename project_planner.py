"""Deterministic, evidence-gated priority ranking and editable charter draft.
No model output is accepted as a verified financial result or an approved project.
"""
from pydantic import BaseModel, Field

FACTORS=('profit','liquidity','delivery','risk','feasibility')
WEIGHTS={'profit':25,'liquidity':20,'delivery':25,'risk':20,'feasibility':10}

class Rating(BaseModel):
    value: int = Field(ge=0,le=5)
    rationale: str = Field(min_length=5,max_length=1500)
    evidence_ids: list[str] = Field(default_factory=list,max_length=30)

class CandidateRating(BaseModel):
    candidate_id: str
    ratings: dict[str,Rating]

class RankRequest(BaseModel):
    analysis: dict
    ratings: list[CandidateRating]

class DraftRequest(BaseModel):
    analysis: dict
    ratings: list[CandidateRating]
    selected_id: str | None = None
    company_id: str = Field(min_length=1,max_length=100)
    diagnostic_id: str = Field(min_length=1,max_length=100)


def weighted_score(values):
    return round(sum(values[k] * WEIGHTS[k] / 5 for k in FACTORS), 2)


def rank(analysis, ratings):
    from project_candidates import prepare_candidates
    candidates=prepare_candidates(analysis)['candidates']
    rating_map={r.candidate_id:r for r in ratings}
    if len(rating_map)!=len(ratings):raise ValueError('Duplirane ocjene kandidata')
    if set(rating_map)-{c['id'] for c in candidates}:raise ValueError('Nepostojeći kandidat')
    out=[]
    for c in candidates:
        row=dict(c)
        r=rating_map.get(c['id'])
        if r is None or set(r.ratings)!=set(FACTORS):
            row.update(score=None,rank_status='NEDOSTAJU_OCJENE',unverified_factors=list(FACTORS))
        else:
            row['score']=weighted_score({k: r.ratings[k].value for k in FACTORS})
            row['rank_status']='PROCJENA_KONSULTANTA_NIJE_VERIFICIRANA'
            row['unverified_factors']=[k for k in FACTORS if not r.ratings[k].evidence_ids]
            row['factor_assessments']={k:r.ratings[k].model_dump() for k in FACTORS}
        out.append(row)
    out.sort(key=lambda x:(x['score'] is None,-(x['score'] or 0),x['id']))
    for i,c in enumerate(out):c['rank']=i+1 if c['score'] is not None else None
    return {'candidates':out,'weights':WEIGHTS,'approval':'REQUIRED',
            'ranking_note':'Ocjene su procjene konsultanta, a ne dokaz finansijske koristi; nepotkrijepljene ocjene zahtijevaju validaciju.'}


def draft(payload:DraftRequest):
    ranked=rank(payload.analysis,payload.ratings)['candidates']
    eligible=[c for c in ranked if c['score'] is not None]
    if not eligible:raise ValueError('Prije izrade nacrta ocijenite svih pet faktora najmanje jednog kandidata')
    if payload.selected_id:
        chosen=next((c for c in eligible if c['id']==payload.selected_id),None)
        if chosen is None:raise ValueError('Odabrani kandidat nije ocijenjen')
    else:chosen=eligible[0]
    checks=['Potvrditi početno stanje KPI i izvor podataka',
            'Provjeriti hipoteze i uzroke na stvarnim podacima',
            'Odobriti brojčane ciljeve prije implementacije']
    if chosen.get('required_validation'):checks.insert(0,chosen['required_validation'])
    if chosen['unverified_factors']:checks.append('Dokumentovati dokaze za faktore: '+', '.join(chosen['unverified_factors']))
    charter={
      'problem':(chosen['why'] or 'Potrebna je provjera dijagnostičkog nalaza i uzroka.'),
      'objective':'Validirati problem, potvrditi početno stanje i odobriti mjerljiv cilj projekta.',
      'scope':'Faza validacije i priprema ograničenog operativnog pilota.',
      'methodology':'DMAIC — Define/Measure; konsultant bira konačnu metodologiju',
      'assumptions':['Projektni prijedlog je zasnovan na dijagnostičkim hipotezama, ne na nezavisnoj verifikaciji.'],
      'required_checks':checks,
      'baseline_verified':False,'targets_approved':False,'checks_completed':False,
      'activities':[
        {'phase':'Validacija','name':'Prikupiti izvorne podatke i dokaze','owner':'Konsultant / klijent','due':'Predložiti nakon pregleda'},
        {'phase':'Analiza','name':'Potvrditi uzroke i početne KPI vrijednosti','owner':'Konsultant','due':'Predložiti nakon validacije'},
        {'phase':'Odobrenje','name':'Odobriti cilj, plan, resurse i uslove pilota','owner':'Konsultant','due':'Prije implementacije'}],
      'kpis':[],'financial_effects':[]}
    return {'company_id':payload.company_id,'diagnostic_id':payload.diagnostic_id,
      'title':chosen['title'],'charter':charter,'selected_candidate':chosen['id'],
      'candidate_score':chosen['score'],'status':'DRAFT_REQUIRES_CONSULTANT_APPROVAL',
      'note':'Deterministički preliminarni nacrt; nije AI-generisan kompletan Project Execution Pack.'}
