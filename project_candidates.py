"""Evidence-aware candidate preparation from a v3 analysis; never claims ROI or validated root causes."""
from pydantic import BaseModel, Field

class CandidateInput(BaseModel):
    analysis: dict


def prepare_candidates(analysis: dict):
    ai=analysis.get('ai') or analysis.get('narrative') or {}
    if not isinstance(ai,dict): ai={}
    decisions=ai.get('decisions') or analysis.get('decisions') or analysis.get('priority_decisions') or []
    criteria=analysis.get('criteria') or []
    valid={str(c.get('code')) for c in criteria if isinstance(c,dict)}
    if not valid and analysis.get('version')=='2.0':
        from diagnostic_engine import CODES
        valid=set(CODES)
    result=[]
    for i,d in enumerate(decisions[:10]):
        if not isinstance(d,dict):continue
        title=str(d.get('title') or '').strip()[:180]
        if not title:continue
        codes=[str(c) for c in (d.get('criterion_codes') or d.get('criteria') or []) if str(c) in valid]
        result.append({'id':f'C{i+1}', 'title':title,
          'why':str(d.get('why') or d.get('evidence_needed') or '')[:1200],
          'criterion_codes':codes,
          'hypothesis_status':'NEPOTVRĐENO',
          'financial_impact':'NIJE_VERIFICIRANO',
          'delivery_impact':'ZA_PROCJENU',
          'liquidity_impact':'ZA_PROCJENU',
          'risk':'ZA_PROCJENU',
          'feasibility':'ZA_PROCJENU',
          'priority':'PRIJEDLOG_AI_BEZ_VALIDIRANOG_RANGIRANJA',
          'required_validation':str(d.get('decision_evidence') or d.get('evidence_needed') or '')[:1200]})
    return {'status':'DRAFT_NOT_APPROVED','candidates':result,
      'selection_policy':'Konsultant potvrđuje prioritet nakon procjene profita, likvidnosti, isporuke, rizika i izvedivosti.',
      'independently_verified':False}
