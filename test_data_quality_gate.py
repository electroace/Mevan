import unittest
from data_quality_gate import check_record,check_batch
class TestQualityGate(unittest.TestCase):
 def test_simulated_cannot_verify(self):
  x=check_record({'criterion_id':'P12','score':2,'is_simulated':True,'verification_status':'provjereno'})
  self.assertEqual(x['status'],'blokirano');self.assertFalse(x['independently_verified'])
 def test_unknown_not_zero(self):
  self.assertEqual(check_record({'criterion_id':'F05','score':0,'verification_status':'nema_podataka'})['status'],'blokirano')
 def test_na_approval(self):
  self.assertEqual(check_record({'criterion_id':'F05','verification_status':'nije_primjenjivo'})['status'],'blokirano')
 def test_invalid_ratio(self):
  self.assertEqual(check_record({'criterion_id':'O01','score':2,'verification_status':'samoprocjena','kpi_ratio':True,'denominator':0})['status'],'blokirano')
 def test_duplicate(self):
  self.assertEqual(check_batch([{'criterion_id':'F05'},{'criterion_id':'F05'}])['blocked'],1)
 def test_simulation_labeled(self):
  x=check_record({'criterion_id':'F06','score':2,'verification_status':'simulacija','is_simulated':True})
  self.assertEqual(x['status'],'prolaz');self.assertFalse(x['independently_verified'])
 def test_benefit_requires_basis(self):
  self.assertEqual(check_record({'criterion_id':'F06','score':2,'verification_status':'samoprocjena','financial_benefit':100})['status'],'blokirano')
if __name__=='__main__': unittest.main()
