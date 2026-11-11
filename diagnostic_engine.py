"""MEVAN v2 deterministic, auditable diagnostic support. Not an AI or professional sign-off."""
import math
from collections import defaultdict

DIMENSIONS={'F':'Finansije','O':'Operacije','P':'Planiranje','L':'Ljudi','M':'Upravljanje'}
CODES={f'{d}{i:02d}' for d,n in [('F',12),('O',15),('P',12),('L',10),('M',12)] for i in range(1,n+1)}
# Causal hypotheses: never presented as proven without direct evidence.
CHAINS=[
 ('Nestabilan plan i kapacitet',('P02','P03','P04','P09','O11'), 'Provjeriti promjene plana, raspoloživost materijala i opterećenje uskog grla.', 'Direktor operacija / planiranje'),
 ('Gubici kvaliteta',('O05','F06','O08','M06'), 'Uporediti škart po uzroku, proizvodu i seriji sa stvarnim troškom dorade.', 'Kvalitet / proizvodnja / kontroling'),
 ('Zalihe i likvidnost',('F07','F08','P07','P08'), 'Provjeriti tačnost ERP zaliha, starost, obrt i cash-flow.', 'Finansije / SCM'),
 ('Oprema i zastoji',('O03','O04','O07','O10'), 'Potvrditi evidenciju zastoja, usko grlo i uticaj na isporuku.', 'Održavanje / proizvodnja'),
 ('Upravljačka disciplina',('L02','M03','M06','M07'), 'Provjeriti vlasništvo nad KPI, eskalacije i zatvaranje ponovljenih problema.', 'COO / rukovodioci')]

def num(value):
    try:
        x=float(value)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):return None

def analyze(payload):
    assessments=payload.get('assess',{})
    if not isinstance(assessments,dict):raise ValueError('Neispravne procjene')
    rows=[]; dimensions={d:{'applicable':0,'verified':0,'sum':0,'unverified':0,'na':0} for d in DIMENSIONS}
    for code in sorted(CODES):
        a=assessments.get(code,{})
        if not isinstance(a,dict):a={}
        dim=dimensions[code[0]]
        if a.get('applicable')=='no':
            dim['na']+=1;continue
        dim['applicable']+=1
        score=num(a.get('score'))
        proof=a.get('proof')
        evidence=str(a.get('evidence') or '').strip()
        # Assessment/documentation coverage only. NEVER infer independent verification from entered text.
        confirmed=(proof=='confirmed' and score is not None and score.is_integer() and 0<=score<=5 and bool(evidence))
        if confirmed:
            dim['verified']+=1;dim['sum']+=score
        else:dim['unverified']+=1
        rows.append({'code':code,'score':int(score) if score is not None and score.is_integer() and 0<=score<=5 else None,'status':'documented_unverified' if confirmed else 'unverified',
          'evidence':evidence[:1200], 'finding':str(a.get('finding') or '')[:1200], 'kpi':str(a.get('kpi') or '')[:500]})
    bycode={r['code']:r for r in rows}
    for d,v in dimensions.items():
        v['index']=round(20*v['sum']/v['verified'],1) if v['verified'] else None
        del v['sum']
    confirmed=[r for r in rows if r['status']=='documented_unverified']
    total=round(20*sum(r['score'] for r in confirmed)/len(confirmed),1) if confirmed else None
    # Risk triggers override maturity ranking; no financial inference.
    critical=[]
    for code in ('O14','L09','M08'):
        r=bycode.get(code)
        if r and r['status']=='documented_unverified' and r['score']<=2:
            critical.append({'code':code,'reason':'Potencijalni sigurnosni ili kontinuitetni rizik – provjeriti odmah; nije dokaz incidenta.'})
    chains=[]
    for title,codes,check,owner in CHAINS:
        weak=[c for c in codes if c in bycode and bycode[c]['status']=='documented_unverified' and bycode[c]['score']<=2]
        if len(weak)>=2:
            chains.append({'title':title,'criteria':weak,'status':'hypothesis','verification':check,'owner':owner,'priority':len(weak)})
    chains.sort(key=lambda x:-x['priority'])
    weak=sorted((r for r in confirmed if r['score']<=2),key=lambda x:(x['score'],x['code']))
    decisions=[]
    for c in chains[:3]:
        decisions.append({'title':'Provjeriti: '+c['title'],'criteria':c['criteria'],'owner':c['owner'],'deadline_days':30,'kpi':'Definisati početnu vrijednost i cilj nakon potvrde','evidence_needed':c['verification'],'status':'hypothesis'})
    if not decisions and weak:
        for r in weak[:3]:decisions.append({'title':'Potvrditi uzrok odstupanja '+r['code'],'criteria':[r['code']],'owner':'Imenovati odgovornu funkciju','deadline_days':30,'kpi':'Definisati početnu vrijednost','evidence_needed':'Provjeriti izvorni dokument i trend KPI','status':'hypothesis'})
    effects=[]; excluded=[]; seen=set()
    for item in payload.get('effects',[])[:200]:
        if not isinstance(item,dict):continue
        eid=str(item.get('id',''))[:100]
        category=item.get('category')
        annual=num(item.get('annual'));oneoff=num(item.get('oneoff'))
        overlap=str(item.get('overlap') or '').strip()
        basis=str(item.get('evidence') or '').strip()
        # Require documented calculation inputs, not only a text label or status.
        baseline=num(item.get('baseline'));target=num(item.get('target'));unit_value=num(item.get('unit_value'))
        period=str(item.get('period') or '').strip()
        expected=abs(baseline-target)*unit_value if baseline is not None and target is not None and unit_value is not None else None
        declared=oneoff if category=='working_capital' else annual
        calculation_ok=(expected is not None and declared is not None and abs(expected-declared)<=max(1,abs(declared)*0.01))
        ready=(calculation_ok and item.get('status')=='verified' and bool(basis) and bool(period) and baseline is not None and target is not None and unit_value is not None and not overlap and category in ('hard','avoidance','contribution','working_capital') and (annual is not None and annual>=0) and (oneoff is not None and oneoff>=0) and eid not in seen)
        seen.add(eid)
        obj={'id':eid,'name':str(item.get('name') or '')[:200],'category':category,'annual':annual or 0,'oneoff':oneoff or 0,'status':'pending_independent_review' if ready else 'excluded','reason':'Aritmetički usklađeno, ali nije nezavisno provjereno niti odobreno' if ready else 'Nedostaje dokaz/osnovica/period, izračun nije usklađen ili postoji preklapanje'}
        excluded.append(obj)  # No automatic monetary approval from self-reported fields
    sums={k:{'annual':0,'oneoff':0} for k in ('hard','avoidance','contribution','working_capital')}
    for x in effects:
        sums[x['category']]['annual']+=x['annual'];sums[x['category']]['oneoff']+=x['oneoff']
    return {'version':'2.0','label':'AUTOMATSKA PODRŠKA – NIJE ODOBRENI NALAZ','index':total,'index_status':'SELF_ASSESSED_NOT_INDEPENDENTLY_VERIFIED','independently_verified_criteria':0,'dimensions':dimensions,'coverage':{'confirmed':len(confirmed),'applicable':len(rows),'unverified':len(rows)-len(confirmed),'independently_verified':0,'confirmed_meaning':'popunjena procjena sa tekstom dokaza; nije nezavisna verifikacija'},'critical':critical,'causal_hypotheses':chains,'priority_decisions':decisions,'weak_criteria':[{'code':r['code'],'score':r['score']} for r in weak[:12]],'finance':{'eligible':effects,'excluded':excluded,'totals':sums,'warning':'Potvrđeni finansijski efekti: 0 KM. Prikazani scenariji nisu odobreni. EBITDA, izbjegnuti trošak i jednokratni obrtni kapital ne sabiraju se. Nije izvršena nezavisna provjera.'},'limitations':['Potvrđeno znači dokumentovano u samoprocjeni, ne nezavisno verificirano; indeks je simulirana samoprocjena.','Uzročne veze su hipoteze, a ne dokazani uzroci.','Nijedna preporuka nije automatski odobrena za klijenta.']}
