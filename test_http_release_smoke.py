from pathlib import Path

def test_http_smoke_script_is_bundled():
    p=Path(__file__).with_name('http_release_smoke.py')
    assert p.exists()
    text=p.read_text()
    assert 'TemporaryDirectory' in text and 'MEVAN_DB' in text
    assert 'OPENAI_API_KEY' not in text
