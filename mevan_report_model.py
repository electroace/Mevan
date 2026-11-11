"""Verzionisani obračun za nove zaključane izvještaje, bez izmjene starih snimaka."""
from diagnostic_engine import analyze

DEMO_LABEL = 'DEMO — simulirani podaci'


def has_simulated_inputs(company, diagnostic):
    assess=diagnostic.get('assess',{})
    if not isinstance(assess,dict):raise ValueError('Neispravan zapis ulaznih ocjena')
    return (company.get('id')=='metalpro-demo' or any(
        isinstance(a,dict) and (a.get('is_simulated') is True or 'simulacij' in str(a.get('evidence','')).casefold() or 'simuliran' in str(a.get('evidence','')).casefold())
        for a in assess.values()))


def freeze_model(diagnostic):
    assessments={}
    for row in diagnostic['quality_records']:
        assessments[row['criterion_id']] = ({'applicable':'no'} if row['verification_status']=='nije_primjenjivo' else
            {'score':row['score'],'proof':'confirmed','evidence':row['evidence_reference']})
    result=analyze({'assess':assessments,'effects':diagnostic.get('effects',[])})
    return {'version':2,'result':result}
