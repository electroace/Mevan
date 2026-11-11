import pytest
from pydantic import ValidationError
from project_actuals import ActualIn,summarize

def entry(**kwargs):
    return dict(period='2026-11',name='Smanjenje škarta',category='operating_saving',amount_km='120.50',evidence_reference='ERP izvještaj 11',calculation_note='Razlika stvarnih troškova u mjesecu',source_owner='Kontroling',**kwargs)

def test_independent_verification_not_claimed():
    with pytest.raises(ValidationError):ActualIn.model_validate(entry(independent_verification=True))

def test_evidence_required():
    with pytest.raises(ValidationError):ActualIn.model_validate({**entry(),'evidence_reference':''})

def test_pending_not_confirmed():
    x=ActualIn.model_validate(entry()).model_dump(mode='json')
    s=summarize([x]);assert s['consultant_confirmed_recurring_km']==0 and s['pending_count']==1

def test_confirmed_separates_working_capital():
    a=ActualIn.model_validate(entry(consultant_confirmed=True)).model_dump(mode='json')
    b=ActualIn.model_validate({**entry(consultant_confirmed=True),'category':'working_capital_release','amount_km':'160000'}).model_dump(mode='json')
    s=summarize([a,b]);assert s['consultant_confirmed_recurring_km']==120.5 and s['consultant_confirmed_one_time_working_capital_km']==160000 and s['independently_verified_km']==0
