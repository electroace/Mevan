import unittest
from project_planner import RankRequest,DraftRequest,rank,draft
A={'criteria':[{'code':'P01'}], 'decisions':[{'title':'Planiranje proizvodnje','why':'Neujednačeni planovi proizvodnje','criterion_codes':['P01']},{'title':'Smanjenje škarta','why':'Simulirani škart iznad plana'}]}
def rating(cid,v):
 return {'candidate_id':cid,'ratings':{k:{'value':v,'rationale':'Stručna procjena bez dokaza'} for k in ('profit','liquidity','delivery','risk','feasibility')}}
class TestPlanner(unittest.TestCase):
 def test_ranking_is_data_driven_not_fixed(self):
  r=rank(A,RankRequest(analysis=A,ratings=[rating('C1',1),rating('C2',4)]).ratings)
  self.assertEqual(r['candidates'][0]['title'],'Smanjenje škarta')
  self.assertEqual(r['candidates'][0]['score'],80)
  self.assertEqual(len(r['candidates'][0]['unverified_factors']),5)
 def test_no_fabricated_financials_or_approved_baseline(self):
  d=draft(DraftRequest(analysis=A,ratings=[rating('C1',4)],company_id='demo',diagnostic_id='d1'))
  self.assertEqual(d['charter']['financial_effects'],[])
  self.assertFalse(d['charter']['baseline_verified'])
  self.assertEqual(d['status'],'DRAFT_REQUIRES_CONSULTANT_APPROVAL')
 def test_unrated_candidate_not_selected(self):
  d=draft(DraftRequest(analysis=A,ratings=[rating('C2',2)],company_id='demo',diagnostic_id='d1'))
  self.assertEqual(d['title'],'Smanjenje škarta')
 def test_invalid_rating(self):
  with self.assertRaises(ValueError):RankRequest(analysis=A,ratings=[rating('C1',7)])
if __name__=='__main__':unittest.main()
