from release_preflight import check_bundle, check_runtime

def test_deployment_bundle_contains_all_modules():
    assert check_bundle() == []

def test_runtime_rejects_missing_secrets(monkeypatch):
    for key in ('MEVAN_ADMIN_PASSWORD', 'MEVAN_SESSION_SECRET', 'MEVAN_PUBLIC_ORIGIN', 'MEVAN_ALLOWED_HOSTS', 'MEVAN_SECURE_COOKIE'):
        monkeypatch.delenv(key, raising=False)
    assert len(check_runtime()) >= 4

def test_runtime_accepts_valid_test_settings(monkeypatch):
    for key, value in {
        'MEVAN_ADMIN_PASSWORD': 'A_unique_random_password_123!',
        'MEVAN_SESSION_SECRET': 'a'*48,
        'MEVAN_PUBLIC_ORIGIN': 'https://mevan-test.invalid',
        'MEVAN_ALLOWED_HOSTS': 'mevan-test.invalid',
        'MEVAN_SECURE_COOKIE': '1',
    }.items():
        monkeypatch.setenv(key, value)
    assert check_runtime() == []
