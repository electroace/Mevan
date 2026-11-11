"""TEST-only verified snapshot export and guarded restore for revisioned workspaces."""
import hashlib
import json
import sqlite3
from mevan_sync_guard import read_test_workspace, save_test_workspace, RevisionConflict, InvalidWorkspace


class BackupError(Exception):
    pass


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def export_snapshot(db: sqlite3.Connection) -> dict:
    state = read_test_workspace(db)
    if state["workspace"] is None:
        raise BackupError("Nema TEST podataka")
    payload = {"format": "mevan-test-snapshot-v1", "revision": state["revision"], "workspace": state["workspace"]}
    return {"payload": payload, "sha256": hashlib.sha256(canonical(payload)).hexdigest()}


def verify_snapshot(snapshot: dict) -> dict:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("payload"), dict):
        raise BackupError("Neispravan snapshot")
    payload = snapshot["payload"]
    if payload.get("format") != "mevan-test-snapshot-v1":
        raise BackupError("Nepodržan format")
    if type(payload.get("revision")) is not int or payload["revision"] < 1:
        raise BackupError("Neispravna revizija")
    digest = hashlib.sha256(canonical(payload)).hexdigest()
    if not isinstance(snapshot.get("sha256"), str) or digest != snapshot["sha256"]:
        raise BackupError("Neispravan SHA-256")
    return payload


def restore_snapshot(db: sqlite3.Connection, snapshot: dict, expected_revision: int, confirm: str) -> int:
    """Explicit TEST restore; refuses stale revision and corrupt snapshot.

    Callers must export and securely retain a pre-restore snapshot before use.
    """
    if confirm != "VRATI-TEST-PODATKE":
        raise BackupError("Nedostaje izričita potvrda")
    payload = verify_snapshot(snapshot)
    try:
        return save_test_workspace(db, payload["workspace"], expected_revision)
    except (RevisionConflict, InvalidWorkspace, ValueError) as exc:
        raise BackupError(str(exc)) from exc
