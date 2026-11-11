"""Exercise the actual Word harness and fail-closed checks, not a copy of it."""
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).parent


def test_extractor_handles_multiple_scripts_and_rejects_broken_main():
    script=r'''
const assert=require('node:assert/strict');
const {extractMainScript}=require('./qa_word_reports.js');
const main='const CRITERIA=[]; function exportDOCX(){} function cloudBoot(){} cloudBoot();\nconst afterBoot=42;';
assert.equal(extractMainScript('<script>'+main+'</script><aside>HTML</aside><script>throw Error("ne izvršavati")</script>'),main);
assert.throws(()=>extractMainScript('<script>const CRITERIA=[];function exportDOCX(){</script>'));
assert.throws(()=>extractMainScript('<script>'+main+'</script><script>'+main+'</script>'));
assert.throws(()=>extractMainScript('<script>'+main));
'''
    subprocess.run(['node','-e',script],cwd=ROOT,check=True,capture_output=True,text=True)


def test_twelve_word_reports_and_corruption_checks(tmp_path):
    env={**os.environ,'MEVAN_WORD_QA_DIR':str(tmp_path/'word')}
    generated=subprocess.run(['node','qa_word_reports.js'],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert '12 DOCX' in generated.stdout
    subprocess.run([sys.executable,'qa_word_reports.py'],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    # Never overwrite earlier successful artifacts on a repeated run.
    assert subprocess.run(['node','qa_word_reports.js'],cwd=ROOT,env=env,capture_output=True).returncode != 0
    file=next((tmp_path/'word').glob('*.docx'))
    with zipfile.ZipFile(file) as z:
        entries={name:z.read(name) for name in z.namelist()}
    entries['word/document.xml']=entries['word/document.xml'].replace(b'Neodobreno / promijenjeni podaci.',b'Interno odobren simulacijski nacrt')
    with zipfile.ZipFile(file,'w') as z:
        for name,data in entries.items():z.writestr(name,data)
    assert subprocess.run([sys.executable,'qa_word_reports.py'],cwd=ROOT,env=env,capture_output=True).returncode != 0
