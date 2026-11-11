import pytest
from pydantic import ValidationError
from project_finance import FinancialModel,calculate

def sample():
    def s(name):
        return {'name':name,'implementation_cost_km':10000,'annual_running_cost_km':2000,
          'benefits':[{'name':'Smanjenje škarta','category':'operating_saving','amount_km':12000,'source':'Simulirani podaci','assumption':'Pilot procjena'},
          {'name':'Obrtni kapital','category':'working_capital_release','amount_km':160000,'source':'Simulirani podaci','assumption':'Zalihe'}]}
    return {'scenarios':[s(n) for n in ['pesimistični','realni','optimistični']]}

def test_financial_separation():
    r=calculate(FinancialModel.model_validate(sample()))['scenarios'][0]
    assert r['annual_net_benefit_km']==10000
    assert r['one_time_working_capital_release_km']==160000
    assert r['simple_annual_roi_percent']==100
    assert r['simple_payback_months']==12
    assert r['confirmed_annual_benefit_km']==0

def test_missing_scenario_rejected():
    d=sample();d['scenarios'].pop()
    with pytest.raises(ValidationError):FinancialModel.model_validate(d)

def test_unverified_claim_cannot_be_confirmed():
    d=sample();d['scenarios'][0]['benefits'][0]['evidence_status']='independently_verified'
    with pytest.raises(ValidationError):FinancialModel.model_validate(d)

def test_no_payback_on_negative_net():
    d=sample();d['scenarios'][0]['annual_running_cost_km']=30000
    r=calculate(FinancialModel.model_validate(d))['scenarios'][0]
    assert r['simple_payback_months'] is None

def test_no_roi_when_no_investment():
    d=sample();d['scenarios'][0]['implementation_cost_km']=0
    r=calculate(FinancialModel.model_validate(d))['scenarios'][0]
    assert r['simple_annual_roi_percent'] is None

def test_duplicate_benefit_rejected():
    d=sample();d['scenarios'][0]['benefits'].append(d['scenarios'][0]['benefits'][0].copy())
    with pytest.raises(ValidationError):FinancialModel.model_validate(d)
