"""Financial scenario calculations: estimates only, never verified actuals."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pydantic import BaseModel, Field, model_validator
from typing import Literal

class Benefit(BaseModel):
    name: str = Field(min_length=3,max_length=160)
    category: Literal['operating_saving','contribution_margin','avoided_cost','working_capital_release']
    amount_km: Decimal = Field(ge=0,le=100000000000)
    source: str = Field(min_length=3,max_length=500)
    assumption: str = Field(min_length=3,max_length=500)
    evidence_status: Literal['estimated','consultant_confirmed','independently_verified'] = 'estimated'
    # Confirmation must occur in a separate evidence workflow, never through this calculator.
    @model_validator(mode='after')
    def no_false_confirmation(self):
        if self.evidence_status != 'estimated':
            raise ValueError('Kalkulator scenarija prihvata samo procjene, ne potvrđene efekte')
        return self

class Scenario(BaseModel):
    name: Literal['pesimistični','realni','optimistični']
    implementation_cost_km: Decimal = Field(ge=0,le=100000000000)
    annual_running_cost_km: Decimal = Field(ge=0,le=100000000000)
    benefits: list[Benefit] = Field(min_length=1,max_length=30)

class FinancialModel(BaseModel):
    scenarios: list[Scenario] = Field(min_length=3,max_length=3)
    currency: Literal['KM'] = 'KM'
    @model_validator(mode='after')
    def check_names(self):
        if {s.name for s in self.scenarios} != {'pesimistični','realni','optimistični'}:
            raise ValueError('Obavezna su tri različita scenarija')
        for s in self.scenarios:
            names=[b.name.strip().casefold() for b in s.benefits]
            if len(names)!=len(set(names)):
                raise ValueError('Duplirani naziv koristi u scenariju')
        return self

def money(d):
    return float(d.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))

def calculate(model:FinancialModel):
    output=[]
    for s in model.scenarios:
        recurring=sum((b.amount_km for b in s.benefits if b.category!='working_capital_release'),Decimal(0))
        wc=sum((b.amount_km for b in s.benefits if b.category=='working_capital_release'),Decimal(0))
        net=recurring-s.annual_running_cost_km
        cap=s.implementation_cost_km
        # Return on initial implementation investment, excluding one-off working capital.
        roi=money(net/cap*100) if cap>0 else None
        payback=money(cap/net*12) if cap>0 and net>0 else None
        output.append({'name':s.name,'annual_gross_benefit_km':money(recurring),
            'annual_running_cost_km':money(s.annual_running_cost_km),
            'annual_net_benefit_km':money(net),
            'one_time_working_capital_release_km':money(wc),
            'implementation_cost_km':money(cap),
            'simple_annual_roi_percent':roi,'simple_payback_months':payback,
            'status':'estimated','confirmed_annual_benefit_km':0,
            'confirmed_one_time_benefit_km':0})
    return {'currency':'KM','scenarios':output,
      'methodology':'Jednostavni godišnji ROI = neto godišnji efekat / jednokratni trošak implementacije. Povrat (mjeseci) = trošak implementacije / neto godišnji efekat × 12. Obrtni kapital je odvojen i isključen iz ROI i povrata. Bez diskontovanja i vremenskog rasporeda efekata.',
      'warning':'Svi rezultati su scenarijske procjene, ne potvrđeni ili ostvareni efekti.'}
