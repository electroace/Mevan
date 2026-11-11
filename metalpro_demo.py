"""METALPRO DEMO: synthetic 61-criterion assessment, no independently verified findings."""
from diagnostic_engine import CODES, analyze
from project_candidates import prepare_candidates
from project_planner import FACTORS, CandidateRating, Rating, DraftRequest, draft
from project_finance import FinancialModel, calculate

DIMENSION_SUMS={'F':23,'O':26,'P':21,'L':21,'M':20}
ESTIMATES=[('Škart','operating_saving',9450),('Zastoji','contribution_margin',13728),('Promjene serija','contribution_margin',9405),('Hitni transport','avoided_cost',12096),('Radni sati','avoided_cost',7488),('Obrtni kapital','working_capital_release',160000)]

def diagnostic():
    assess={}
    for dim,total in DIMENSION_SUMS.items():
        codes=sorted(c for c in CODES if c.startswith(dim))
        base=total//len(codes); extra=total%len(codes)
        for i,code in enumerate(codes):
            assess[code]={'score':base+(i<extra),'proof':'confirmed','evidence':'SIMULIRANI intervju — nije nezavisno verificirano','finding':'SIMULIRANA procjena, potrebno potvrditi izvorne podatke'}
    result=analyze({'assess':assess,'effects':[]})
    assert result['coverage']['confirmed']==61
    assert result['index']==36.4
    assert result['independently_verified_criteria']==0
    return result

def analysis():
    return diagnostic()

def candidate_ratings(analysis_data):
    candidates=prepare_candidates(analysis_data)['candidates']
    if not candidates:raise ValueError('Dijagnostika nije predložila kandidate')
    # Demo consultant scores are illustrative, never evidence-backed.
    return [CandidateRating(candidate_id=c['id'],ratings={k:Rating(value=3,rationale='Simulirana procjena konsultanta; bez nezavisnog dokaza') for k in FACTORS}) for c in candidates]

def project_draft():
    a=analysis(); return draft(DraftRequest(analysis=a,ratings=candidate_ratings(a),company_id='METALPRO-DEMO',diagnostic_id='METALPRO-61-DEMO'))

def finance_model():
    scales={'pesimistični':0.5,'realni':1.0,'optimistični':1.3}
    return FinancialModel.model_validate({'scenarios':[{'name':name,'implementation_cost_km':15000,'annual_running_cost_km':2500,'benefits':[{'name':label,'category':cat,'amount_km':round(amount*factor,2),'source':'METALPRO DEMO — simulacija','assumption':'Hipoteza bez verifikacije'} for label,cat,amount in ESTIMATES]} for name,factor in scales.items()]})

def demo_summary():
    a=analysis();p=project_draft();f=calculate(finance_model())
    return {'company':'METALPRO DEMO','criteria_assessed':61,'criteria_independently_verified':0,'maturity_index':a['index'],'dimensions':{k:v['index'] for k,v in a['dimensions'].items()},'candidate_count':len(prepare_candidates(a)['candidates']),'proposed_project':p['title'],'project_status':p['status'],'financial_scenarios':f['scenarios'],'confirmed_annual_km':0,'confirmed_one_time_km':0,'independently_verified_financial_km':0,'limitations':['Simulirani podaci','Nema potvrđenih početnih KPI ni ciljeva','Nema implementacijskog odobrenja','Nema stvarnih sedmičnih mjerenja ili ostvarenih efekata']}

if __name__=='__main__':
 import json
 print(json.dumps(demo_summary(),ensure_ascii=False,indent=2))
