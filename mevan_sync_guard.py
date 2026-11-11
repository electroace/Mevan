"""MEVAN TEST: isolated optimistic-concurrency primitives.

Not wired into production routes. No migrations or existing data writes.
"""
import json
import sqlite3
import time
from typing import Any


class RevisionConflict(Exception):
    """Client revision is stale; caller must reload and reconcile."""


class InvalidWorkspace(Exception):
    """Workspace does not match minimal storage contract."""


def validate_workspace(workspace: Any) -> None:
    if not isinstance(workspace, dict):
        raise InvalidWorkspace("Workspace mora biti objekat")
    companies = workspace.get("companies")
    if not isinstance(companies, list) or not 1 <= len(companies) <= 100:
        raise InvalidWorkspace("Neispravna lista kompanija")
    for company in companies:
        if not isinstance(company, dict) or not isinstance(company.get("diagnostics"), list):
            raise InvalidWorkspace("Neispravna dijagnostika")
        if len(company["diagnostics"]) > 100:
            raise InvalidWorkspace("Previše dijagnostika")
        for diagnostic in company['diagnostics']:
            if not isinstance(diagnostic,dict):continue
            if diagnostic.get('report_mode','real') not in ('real','demo'):
                raise InvalidWorkspace('Nepoznat način izvještaja')
            guided=diagnostic.get('guided',{})
            if not isinstance(guided,dict):raise InvalidWorkspace('Vođeno prikupljanje mora biti objekat')
            if guided.get('current_stage','interview') not in ('interview','documents','visit','evidence','priorities','project','plan'):
                raise InvalidWorkspace('Nepoznat korak vođenog prikupljanja')
            for key in ('owner','start_date','kpi','project_id','selected_candidate'):
                if key in guided and (not isinstance(guided[key],str) or len(guided[key])>4000):
                    raise InvalidWorkspace('Neispravan podatak vođenog projekta')
            records=diagnostic.get('quality_records',[])
            if isinstance(records,list):
                for record in records:
                    if not isinstance(record,dict) or 'collection' not in record:continue
                    sources=record['collection']
                    if not isinstance(sources,dict) or any(key in sources and (not isinstance(sources[key],str) or len(sources[key])>10000) for key in ('interview','documents','visit')):
                        raise InvalidWorkspace('Bilješke intervjua, dokumentacije i obilaska moraju biti tekst do 10000 znakova')


def init_test_store(db: sqlite3.Connection) -> None:
    """Create separate TEST table; does not modify legacy workspace."""
    db.execute("""CREATE TABLE IF NOT EXISTS workspace_test_v2 (
        id INTEGER PRIMARY KEY CHECK (id=1),
        payload TEXT NOT NULL,
        revision INTEGER NOT NULL CHECK (revision >= 1),
        updated INTEGER NOT NULL
    )""")
    db.commit()


def read_test_workspace(db: sqlite3.Connection) -> dict:
    row = db.execute(
        "SELECT payload, revision, updated FROM workspace_test_v2 WHERE id=1"
    ).fetchone()
    return {
        "workspace": json.loads(row[0]) if row else None,
        "revision": row[1] if row else 0,
        "updated": row[2] if row else None,
    }


def save_test_workspace(db: sqlite3.Connection, workspace: dict, expected_revision: int) -> int:
    """Atomic compare-and-swap; raises conflict instead of overwriting."""
    validate_workspace(workspace)
    if type(expected_revision) is not int or expected_revision < 0:
        raise ValueError("expected_revision mora biti nenegativan cijeli broj")
    payload = json.dumps(workspace, ensure_ascii=False, separators=(",", ":"))
    if len(payload.encode("utf-8")) > 4 * 1024 * 1024:
        raise InvalidWorkspace("Prevelika dijagnostika")
    db.execute("BEGIN IMMEDIATE")
    try:
        row = db.execute("SELECT revision FROM workspace_test_v2 WHERE id=1").fetchone()
        current = row[0] if row else 0
        if current != expected_revision:
            raise RevisionConflict(f"Očekivana revizija {expected_revision}, trenutna {current}")
        new_revision = current + 1
        if row:
            db.execute(
                "UPDATE workspace_test_v2 SET payload=?, revision=?, updated=? WHERE id=1",
                (payload, new_revision, int(time.time())),
            )
        else:
            db.execute(
                "INSERT INTO workspace_test_v2(id,payload,revision,updated) VALUES(1,?,?,?)",
                (payload, new_revision, int(time.time())),
            )
        db.commit()
        return new_revision
    except Exception:
        db.rollback()
        raise
