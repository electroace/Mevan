import unittest
from project_candidates import prepare_candidates

class TestCandidates(unittest.TestCase):
 def test_no_invented_financial_values(self):
  x={'criteria':[{'code':'P01'}], 'decisions':[{'title':'Stabilizacija planiranja','criterion_codes':['P01','BAD'],'why':'Simulirana slabost','decision_evidence':'Potrebna provjera'}]}
  r=prepare_candidates(x)
  self.assertEqual(r['status'],'DRAFT_NOT_APPROVED')
  self.assertEqual(len(r['candidates']),1)
  self.assertEqual(r['candidates'][0]['criterion_codes'],['P01'])
  self.assertEqual(r['candidates'][0]['financial_impact'],'NIJE_VERIFICIRANO')
 def test_empty_analysis(self):
  self.assertEqual(prepare_candidates({})['candidates'],[])
if __name__=='__main__': unittest.main()

