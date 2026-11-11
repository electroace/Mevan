from pathlib import Path

def test_dashboard_route_and_page():
    import project_execution
    routes={r.path for r in project_execution.router.routes}
    assert '/api/v4/dashboard' in routes
    page=Path(__file__).parent.joinpath('dashboard_ui.html').read_text()
    assert '/api/v4/dashboard' in page
    assert 'Nezavisno verificirani' in page
    assert 'textContent' in page

def test_dashboard_no_aggregated_financial_amounts():
    import inspect,project_execution
    source=inspect.getsource(project_execution.project_dashboard)
    assert 'consultant_confirmed_entries_count' in source
    assert 'independently_verified_entries_count' in source
    assert 'sum(json.loads' not in source
