"""Regression checks for the step-11 weekly form and API payload."""
from pathlib import Path
from test_project_execution import TestProjectExecution

class TestWeeklyForms(TestProjectExecution):
 def test_weekly_ui_uses_forms_not_json_textareas(self):
  html=Path(__file__).with_name('projects_ui.html').read_text(encoding='utf-8')
  assert 'id="weekActivityRows"' in html
  assert 'id="weekKpiRows"' in html
  assert 'function weeklyPayload()' in html
  assert 'id="weekActivities"' not in html
  assert 'id="weekKpis"' not in html
 def test_weekly_data_roundtrip(self):
  ch=dict(self.charter,baseline_verified=True,targets_approved=True,checks_completed=True,
          activities=[{'title':'Pilot planiranja','owner':'Voditelj proizvodnje'}],
          kpis=[{'name':'OTD','formula':'Na vrijeme / ukupno'}])
  payload={'company_id':'metalpro-demo','diagnostic_id':'demo-weekly','title':'Pilot sa sedmicama','charter':ch}
  pid=self.client.post('/api/v4/projects',json=payload,headers=self.headers).json()['id']
  assert self.client.post(f'/api/v4/projects/{pid}/approve-implementation',headers=self.headers).status_code==200
  week={'week':'2026-W46','activities':[{'title':'Pilot planiranja','status':'in_progress','result':'U toku'}],
        'kpi_measurements':[{'name':'OTD','value':'82%','period':'2026-W46','source':'Simulirana evidencija','verification_status':'consultant_entered'}],
        'blockers':['Simulirani nedostatak podataka'],'decisions':['Prikupiti izvještaj'],'note':'DEMO'}
  assert self.client.post(f'/api/v4/projects/{pid}/weekly-reviews',json=week,headers=self.headers).status_code==201
  actual=self.client.get(f'/api/v4/projects/{pid}').json()['weekly_reviews'][0]
  assert actual['kpi_measurements'][0]['value']=='82%'
  assert actual['activities'][0]['status']=='in_progress'
