import unittest, json
from pydantic import ValidationError
from project_ai_pack import AIPlan, assemble, generate
from project_planner import DraftRequest
from test_project_planner import A, rating

def plan():
 return {'methodology':'DMAIC / TOC pilot','rationale':'Provjera stvarnih uzroka kroz ograničen pilot.',
 'proposed_duration_weeks':12,'hypotheses':['Kapacitet je moguće usko grlo'],
 'validation_checks':['Potvrditi stvarni takt procesa','Prikupiti uzorak dnevnih naloga'],
 'activities':[{'phase':p,'name':'Provjeriti proces i dokumentovati podatke',
 'owner':'Konsultant','due':'Sedmica 1-2','deliverable':'Potpisan pregled podataka',
 'acceptance':'Izvori i uzorak dokumentovani'} for p in ('Define','Measure','Analyze')],
 'kpis':[{'name':'Tačnost plana','formula':'izvršeni nalozi / planirani nalozi',
 'source':'ERP izvještaj','frequency':'Sedmično','owner':'Planer','baseline':None,'target':None}],
 'risks':['Nedostaju dnevni podaci']}
class TestAIProjectPack(unittest.TestCase):
 def setUp(self):
  self.p=DraftRequest(analysis=A,ratings=[rating('C1',4)],company_id='demo',diagnostic_id='d1')
 def test_valid_ai_pack_unapproved(self):
  data=generate(self.p,lambda request:{'choices':[{'message':{'content':json.dumps(plan())}}]})
  self.assertEqual(data['status'],'DRAFT_REQUIRES_CONSULTANT_APPROVAL')
  self.assertFalse(data['charter']['baseline_verified'])
  self.assertEqual(data['charter']['financial_effects'],[])
  self.assertEqual(len(data['charter']['activities']),3)
 def test_reject_fabricated_baseline(self):
  p=plan();p['kpis'][0]['baseline']=98
  with self.assertRaises(ValidationError):AIPlan.model_validate(p)
 def test_reject_extra_financial_claims(self):
  p=plan();p['confirmed_savings']=100000
  with self.assertRaises(ValidationError):AIPlan.model_validate(p)
 def test_selects_ranking_not_fixed_project(self):
  from project_planner import rank
  self.p.ratings=[self.p.ratings[0].model_copy(update={'candidate_id':'C2'})]
  data=generate(self.p,lambda request:{'choices':[{'message':{'content':json.dumps(plan())}}]})
  self.assertEqual(data['title'],'Smanjenje škarta')
if __name__=='__main__':unittest.main()
