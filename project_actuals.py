"""Actual financial effects: separate evidence and explicit consultant confirmation."""
from decimal import Decimal
import json
import unicodedata
from typing import Literal
from pydantic import BaseModel, Field, model_validator

class ActualIn(BaseModel):
    period: str = Field(min_length=4,max_length=40)
    name: str = Field(min_length=3,max_length=160)
    category: Literal['operating_saving','contribution_margin','avoided_cost','working_capital_release']
    amount_km: Decimal = Field(ge=0,le=100000000000,decimal_places=2)
    evidence_reference: str = Field(min_length=3,max_length=1000)
    calculation_note: str = Field(min_length=10,max_length=2000)
    source_owner: str = Field(min_length=2,max_length=160)
    consultant_confirmed: bool = False
    independent_verification: bool = False
    @model_validator(mode='after')
    def safe(self):
        if self.independent_verification:
            raise ValueError('Nezavisna verifikacija zahtijeva odvojeni postupak i nije dostupna u ovom obrascu')
        return self


def canonical_effect(effect: ActualIn) -> str:
    """Stable request identity; numeric JSON spellings are the same amount."""
    data = effect.model_dump(mode='json')
    data['amount_km'] = format(effect.amount_km.quantize(Decimal('0.01')), 'f')
    for key in ('period', 'name', 'evidence_reference', 'calculation_note', 'source_owner'):
        data[key] = unicodedata.normalize('NFC', data[key].strip())
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def summarize(entries):
    recurring=Decimal(0); capital=Decimal(0); pending=0
    for e in entries:
        if not e['consultant_confirmed']:
            pending+=1;continue
        amount=Decimal(str(e['amount_km']))
        if e['category']=='working_capital_release':capital+=amount
        else:recurring+=amount
    return {'consultant_confirmed_recurring_km':float(recurring),'consultant_confirmed_one_time_working_capital_km':float(capital),'independently_verified_km':0,'pending_count':pending,'warning':'Iznosi su evidentirani po periodima, ne predstavljaju automatski godišnji iznos. Konsultantska potvrda nije nezavisna verifikacija; izbjegavati sabiranje preklapajućih perioda.'}
