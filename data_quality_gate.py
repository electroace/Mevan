"""MEVAN test-only deterministic evidence quality gate. Does not certify evidence."""
import math
import re
from diagnostic_engine import CODES

VALID_STATUSES={'nema_podataka','nije_primjenjivo','samoprocjena','dokumentovano_neprovjereno','provjereno','simulacija'}

def valid_na_reason(value):
    if not isinstance(value, str):
        return False
    text=' '.join(value.split())
    words=re.findall(r'[^\W\d_]+',text.casefold())
    return len(text)>=20 and len(words)>=4 and len(set(words))>=3 and not set(words)<={'test','razlog','x','todo','tekst','naknadno'}


def check_record(record, policy_version=2):
    if not isinstance(record,dict): raise ValueError('Zapis mora biti objekat')
    errors=[]; warnings=[]
    code=record.get('criterion_id')
    if code not in CODES: errors.append('Nepoznata šifra kriterija')
    status=record.get('verification_status','nema_podataka')
    if status not in VALID_STATUSES: errors.append('Nepoznat status dokaza')
    simulated=record.get('is_simulated') is True
    if simulated and status=='provjereno': errors.append('Simulirani dokaz ne može biti nezavisno provjeren')
    if simulated and status!='simulacija': warnings.append('Simulacija mora biti jasno označena u izvještaju')
    score=record.get('score')
    if status=='nije_primjenjivo':
        if not str(record.get('na_reason') or '').strip() or not str(record.get('na_approved_by') or '').strip():
            errors.append('N/P zahtijeva obrazloženje i odobrenje')
        if policy_version>=2 and (not valid_na_reason(record.get('na_reason')) or not isinstance(record.get('na_approved_by'),str) or len(record['na_approved_by'].strip())<2):
            errors.append('N/P zahtijeva konkretan razlog (najmanje 20 znakova i 4 riječi) i imenovanog konsultanta')
        if score is not None: errors.append('N/P ne može imati numeričku ocjenu')
    elif status=='nema_podataka':
        if score is not None: errors.append('Nepoznato nije ocjena 0')
    elif not isinstance(score,int) or isinstance(score,bool) or not 0<=score<=5:
        errors.append('Ocjena mora biti cijeli broj od 0 do 5')
    if status=='provjereno':
        required=('assessor_id','evidence_reference','source_id','reference_period_start','reference_period_end','assessment_version','timestamp')
        missing=[k for k in required if not record.get(k)]
        if missing: errors.append('Za provjeren dokaz nedostaje: '+', '.join(missing))
        if not record.get('verification_audit_ref'): errors.append('Nedostaje audit trag provjere')
    if record.get('reference_period_start') and record.get('reference_period_end') and str(record['reference_period_start'])>str(record['reference_period_end']):
        errors.append('Početak perioda je poslije kraja')
    if record.get('kpi_ratio') is True:
        for key in ('unit','numerator_definition','denominator_definition','reference_period_start','reference_period_end'):
            if not record.get(key): warnings.append('Omjerni KPI nema: '+key)
        denom=record.get('denominator')
        if denom is None or isinstance(denom,bool) or not isinstance(denom,(int,float)) or not math.isfinite(denom) or denom==0:
            errors.append('Nazivnik nije validan; KPI se ne smije izračunati')
    benefit=record.get('financial_benefit')
    if benefit is not None:
        for key in ('benefit_formula','benefit_baseline','benefit_period','benefit_validation_status'):
            if record.get(key) is None or record.get(key)=='': errors.append('Finansijska korist nema: '+key)
    return {'criterion_id':code,'status':'blokirano' if errors else ('nepotpuno' if warnings else 'prolaz'), 'errors':errors,'warnings':warnings,'independently_verified':bool(status=='provjereno' and not simulated and not errors),'is_simulated':simulated}

def check_batch(records, policy_version=2):
    if not isinstance(records,list) or len(records)>1000: raise ValueError('Očekuje se lista do 1000 zapisa')
    seen=set(); results=[]
    for r in records:
        result=check_record(r, policy_version=policy_version)
        code=result['criterion_id']
        if code in seen:
            result['errors'].append('Dupli identifikator kriterija')
            result['status']='blokirano';result['independently_verified']=False
        seen.add(code);results.append(result)
    return {'results':results,'blocked':sum(x['status']=='blokirano' for x in results),'verified':sum(x['independently_verified'] for x in results),'note':'Provjera pravila nije nezavisna verifikacija izvora.'}
