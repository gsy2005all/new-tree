from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlmodel import select

from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.check_admin import check_admin_M
from middleware.http_log import http_log_M
from modules.target import (
    Target,
    TargetAuditInput,
    AUDIT_PENDING,
    AUDIT_APPROVED,
    AUDIT_REJECTED,
)
from modules.tree_app_res import TreeAppHttpResponse
from utils.ai_review import ai_review_target

# 管理端路由器，前缀 /admin。
# 依赖顺序很重要：先记录日志 -> 校验登录 -> 校验管理员角色
admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(http_log_M), Depends(check_auth_M), Depends(check_admin_M)],
)


def _apply_audit(target: Target, approved: bool, reason: str | None, admin_id: int | None):
    """把一次审核结果写到 target 上的公共逻辑。admin_id 为 None 表示是 AI 自动审核。"""
    target.audit_status = AUDIT_APPROVED if approved else AUDIT_REJECTED
    target.audit_reason = reason
    target.audited_by = admin_id
    target.audited_at = datetime.now()


@admin_router.get("/targets", response_model=TreeAppHttpResponse)
def list_targets(
    db_handler: DbHandler,
    status: str | None = Query(default=None, description="按审核状态过滤: pending/approved/rejected"),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """管理端查看所有用户提交的打卡目标，可按审核状态过滤并分页。"""
    if status is not None and status not in (AUDIT_PENDING, AUDIT_APPROVED, AUDIT_REJECTED):
        raise HTTPException(400, "无效的审核状态, 仅支持 pending/approved/rejected")

    stmt = select(Target)
    if status is not None:
        stmt = stmt.where(Target.audit_status == status)

    targets = db_handler.exec(stmt.offset(offset).limit(limit)).all()

    # 统计满足条件的总数(用于分页)
    count_stmt = select(Target)
    if status is not None:
        count_stmt = count_stmt.where(Target.audit_status == status)
    total = len(db_handler.exec(count_stmt).all())

    return TreeAppHttpResponse(message="Targets queried successfully", data=list(targets), total=total)


@admin_router.post("/targets/{target_id}/review", response_model=TreeAppHttpResponse)
def review_target(target_id: int, audit_input: TargetAuditInput, db_handler: DbHandler, request: Request):
    """管理员人工审核：通过或驳回某个打卡目标。"""
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(404, "Target not found")

    admin_id = request.state.user_payload.user_id
    _apply_audit(target, audit_input.approved, audit_input.reason, admin_id)

    db_handler.commit()
    db_handler.refresh(target)

    action = "approved" if audit_input.approved else "rejected"
    return TreeAppHttpResponse(message=f"Target {action} successfully", data=[target], total=1)


@admin_router.post("/targets/{target_id}/ai-review", response_model=TreeAppHttpResponse)
def ai_review_single(target_id: int, db_handler: DbHandler):
    """对单个目标执行 AI(规则启发式)自动审核。audited_by 记为 None 表示机器审核。"""
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(404, "Target not found")

    approved, reason = ai_review_target(target)
    _apply_audit(target, approved, reason, admin_id=None)

    db_handler.commit()
    db_handler.refresh(target)

    action = "approved" if approved else "rejected"
    return TreeAppHttpResponse(message=f"AI {action} the target", data=[target], total=1)


@admin_router.post("/targets/ai-review-pending", response_model=TreeAppHttpResponse)
def ai_review_pending(db_handler: DbHandler):
    """批量 AI 审核：把所有待审核(pending)的目标自动判断一遍。"""
    pending = db_handler.exec(select(Target).where(Target.audit_status == AUDIT_PENDING)).all()

    for target in pending:
        approved, reason = ai_review_target(target)
        _apply_audit(target, approved, reason, admin_id=None)

    db_handler.commit()

    return TreeAppHttpResponse(message="AI reviewed all pending targets", data=list(pending), total=len(list(pending)))
