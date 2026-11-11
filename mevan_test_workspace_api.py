"""Isolated TEST API. No automatic mounting, no production data access.

Only create a router when a TEST-only database and authentication/origin
checks have been explicitly supplied by the host application.
"""
import sqlite3
from typing import Callable, Literal
from contextlib import closing
from fastapi.responses import Response
from mevan_test_approval import init_approval_store, approve_workspace, ApprovalError
from mevan_test_report_manifest import ReportPreparationBlocked
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, StrictInt
from mevan_sync_guard import (
    InvalidWorkspace, RevisionConflict, init_test_store,
    read_test_workspace, save_test_workspace,
)


class SaveRequest(BaseModel):
    workspace: dict
    expected_revision: StrictInt


class ApprovalRequest(BaseModel):
    expected_revision: StrictInt
    company_index: StrictInt
    diagnostic_index: StrictInt


def create_test_router(
    db_path: str,
    authorize: Callable[[Request], bool],
    verify_write_origin: Callable[[Request], bool],
    reviewer_id: str = "",
) -> APIRouter:
    """Fail closed: integration MUST provide explicit security callbacks."""
    if not db_path or not callable(authorize) or not callable(verify_write_origin):
        raise ValueError("TEST baza, autentikacija i provjera porijekla su obavezni")

    def require_auth(request: Request):
        if not authorize(request):
            raise HTTPException(401, "Neautorizovan pristup")

    router = APIRouter(
        prefix="/api/test/v2", tags=["isolated-test"],
        dependencies=[Depends(require_auth)],
    )

    def connect():
        return sqlite3.connect(db_path, isolation_level=None, timeout=10)

    @router.get("/workspace")
    def get_test_workspace():
        with closing(connect()) as db:
            init_test_store(db)
            return {**read_test_workspace(db), 'reviewer_id':reviewer_id}

    @router.put("/workspace")
    def put_test_workspace(body: SaveRequest, request: Request):
        if not verify_write_origin(request):
            raise HTTPException(403, "Neispravno porijeklo zahtjeva")
        with closing(connect()) as db:
            init_test_store(db)
            try:
                revision = save_test_workspace(
                    db, body.workspace, body.expected_revision
                )
            except RevisionConflict:
                current = read_test_workspace(db)
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "REVISION_CONFLICT",
                        "current_revision": current["revision"],
                    },
                )
            except (InvalidWorkspace, ValueError) as exc:
                raise HTTPException(status_code=422, detail=str(exc))
        return {"ok": True, "revision": revision}

    @router.post("/approvals")
    def approve(body: ApprovalRequest, request: Request):
        if not verify_write_origin(request):
            raise HTTPException(403, "Neispravno porijeklo zahtjeva")
        with closing(connect()) as db:
            init_test_store(db)
            init_approval_store(db)
            try:
                state = read_test_workspace(db)
                if state["revision"] != body.expected_revision:
                    raise RevisionConflict("Radni prostor je promijenjen")
                try:
                    diagnostic = state["workspace"]["companies"][body.company_index]["diagnostics"][body.diagnostic_index]
                except (KeyError, IndexError, TypeError) as exc:
                    raise ApprovalError("Nepoznata dijagnostika") from exc
                from approved_reports import validate_review
                validate_review(diagnostic, for_approval=True)
                return approve_workspace(db, body.expected_revision, reviewer_id,
                                         body.company_index, body.diagnostic_index)
            except RevisionConflict as exc:
                raise HTTPException(409, str(exc)) from exc
            except (ValueError, TypeError, ApprovalError) as exc:
                raise HTTPException(422, str(exc)) from exc

    @router.get("/approvals")
    def approvals():
        with closing(connect()) as db:
            init_approval_store(db)
            rows = db.execute("SELECT approval_id, workspace_revision, reviewer_id, json_extract(snapshot_json, '$.diagnostic_id'), COALESCE(json_extract(snapshot_json, '$.report_mode'),'real') FROM diagnostic_approvals_test WHERE json_extract(snapshot_json, '$.format') IN ('mevan-bound-approval-v1','mevan-bound-approval-v2') ORDER BY approval_id DESC")
            return [dict(approval_id=id_, revision=rev, reviewer=who, diagnostic_id=diag, report_mode=mode)
                    for id_, rev, who, diag, mode in rows]

    @router.get("/approvals/{approval_id}/{view}/{fmt}")
    def download(request: Request, approval_id: int, view: Literal["executive", "detailed"], fmt: Literal["pdf", "docx"], lang: str | None = None):
        # Jezik fiksnih natpisa: parametar ?lang= ili jezik odabran u aplikaciji. Sadržaj snimka je isti.
        from approved_reports import render
        import mevan_i18n
        language = lang if lang in mevan_i18n.LANGS else mevan_i18n.lang_of(request)
        with closing(connect()) as db:
            init_approval_store(db)
            try:
                content = render(db, approval_id, view, fmt, language)
                from mevan_test_approval import read_approval
                mode=read_approval(db,approval_id)['report_mode']
            except (ApprovalError, ReportPreparationBlocked) as exc:
                raise HTTPException(422, str(exc)) from exc
        mime = "application/pdf" if fmt == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return Response(content, media_type=mime, headers={
            "Content-Disposition": f'attachment; filename="MEVAN_{approval_id}_{"DEMO_" if mode=="demo" else ""}{view}.{fmt}"'
        })

    return router
