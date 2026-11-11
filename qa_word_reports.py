from pathlib import Path
import os
import zipfile
import xml.etree.ElementTree as ET
p=Path(os.environ.get('MEVAN_WORD_QA_DIR', str(Path(__file__).parent/'qa_docx')))
files=list(p.glob('*.docx'))
assert len(files)==12,f'Očekivano 12, pronađeno {len(files)}'
expected={f'MEVAN_{dim}_{view}.docx' for dim in ('Finansije','Operacije','Planiranje','Ljudi','Upravljanje','UKUPNO') for view in ('Detaljni','Sazetak')}
assert {f.name for f in files}==expected,'Nedostaje prikaz ili modul Word izvještaja'
for f in files:
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None,f'ZIP greška: {f.name}'
  for name in ['word/document.xml','word/styles.xml','[Content_Types].xml']:
   ET.fromstring(z.read(name))
  root=ET.fromstring(z.read('word/document.xml'))
  content=' '.join(node.text or '' for node in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
  assert all(x in content for x in ['MEVAN','METALPRO','METALPRO DEMO – SIMULIRANI PODACI','Status analize: Neodobreno / promijenjeni podaci.','Plan prvih 90 dana','Finansijski efekti i ograničenja']),f'Sadržaj: {f.name}'
  assert 'Interno odobren simulacijski nacrt' not in content and 'Interno odobren DEMO' not in content,f'Neočekivano odobrenje: {f.name}'
print('USPJEH: 12/12 DOCX izvještaja – ZIP, XML i osnovni sadržaj')
