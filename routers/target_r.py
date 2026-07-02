from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import func, select

from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.target import AUDIT_APPROVED, Target, TargetInput, TargetUpdateInput
from modules.tree_app_res import TreeAppHttpResponse
from utils.cache import invalidate_prefix

# 创建一个 APIRouter 实例，前缀 /targets，依赖日志与鉴权中间件
target_router = APIRouter(prefix="/targets", dependencies=[Depends(http_log_M), Depends(check_auth_M)])


def _user_targets_key(request: Request, offset: int, limit: int) -> str:
    return f"targets:user:{request.state.user_payload.user_id}:{offset}:{limit}"


# 用装饰器 + 自定义 key 缓存，避免相同用户相同翻页重复查库
from utils.cache import cached as _cached


@target_router.post("/add", response_model=TreeAppHttpResponse)
def add_target(target_input: TargetInput, db_handler: DbHandler, request: Request):
    target_n = Target(**target_input.model_dump())
    target_n.creater_user_id = request.state.user_payload.user_id

    if target_n.remind_time >= target_n.deadline_time:
        raise HTTPException(400, "提醒时间必须早于截止时间")
    if target_n.start_time >= target_n.deadline_time:
        raise HTTPException(400, "开始时间必须早于截止时间")

    # 已取消审核机制：新建目标直接为已通过，立即可打卡
    target_n.audit_status = AUDIT_APPROVED

    db_handler.add(target_n)
    db_handler.commit()
    db_handler.refresh(target_n)

    # 新增目标后，该用户的目标列表缓存需要失效
    invalidate_prefix(f"targets:user:{request.state.user_payload.user_id}:")
    return TreeAppHttpResponse(message="Target added successfully", data=[target_n], total=1)


@target_router.get("/query", response_model=TreeAppHttpResponse)
def query_targets(
    db_handler: DbHandler,
    request: Request,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    uid = request.state.user_payload.user_id
    # 排序：置顶在前（pin_order 降序），普通目标按创建时间（id 升序）
    stmt = (
        select(Target)
        .where(Target.creater_user_id == uid)
        .order_by(Target.pinned.desc(), Target.pin_order.desc(), Target.id)
        .offset(offset)
        .limit(limit)
    )
    target_list = db_handler.exec(stmt).all()

    total = db_handler.exec(
        select(func.count(Target.id)).where(Target.creater_user_id == uid)
    ).one()

    return TreeAppHttpResponse(
        message="Targets queried successfully", data=list(target_list), total=int(total)
    )


@target_router.post("/update/{target_id}", response_model=TreeAppHttpResponse)
def update_target(
    target_id: int, target_update_input: TargetUpdateInput, db_handler: DbHandler, request: Request
):
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    for key, value in target_update_input.model_dump().items():
        if key in target_update_input.update_field:
            setattr(target, key, value)

    # 已取消审核机制：修改后保持已通过状态，无需重新审核
    target.audit_status = AUDIT_APPROVED

    db_handler.commit()
    db_handler.refresh(target)

    invalidate_prefix(f"targets:user:{request.state.user_payload.user_id}:")
    invalidate_prefix(f"stats:target:{target_id}:")
    return TreeAppHttpResponse(message="Target updated successfully", data=[target], total=1)


@target_router.post("/delete/{target_id}", response_model=TreeAppHttpResponse)
def delete_target(target_id: int, db_handler: DbHandler, request: Request):
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    db_handler.delete(target)
    db_handler.commit()

    invalidate_prefix(f"targets:user:{request.state.user_payload.user_id}:")
    invalidate_prefix(f"stats:target:{target_id}:")
    return TreeAppHttpResponse(message="Target deleted successfully", data=[target], total=1)


@target_router.post("/pin/{target_id}", response_model=TreeAppHttpResponse)
def pin_target(target_id: int, db_handler: DbHandler, request: Request):
    """置顶目标：pinned=True，pin_order 设为当前时间戳，使其排在第一页第一条。"""
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    import time
    target.pinned = True
    target.pin_order = int(time.time())
    db_handler.commit()
    db_handler.refresh(target)

    invalidate_prefix(f"targets:user:{request.state.user_payload.user_id}:")
    return TreeAppHttpResponse(message="已置顶", data=[target], total=1)


@target_router.post("/unpin/{target_id}", response_model=TreeAppHttpResponse)
def unpin_target(target_id: int, db_handler: DbHandler, request: Request):
    """取消置顶。"""
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    target.pinned = False
    target.pin_order = 0
    db_handler.commit()
    db_handler.refresh(target)

    invalidate_prefix(f"targets:user:{request.state.user_payload.user_id}:")
    return TreeAppHttpResponse(message="已取消置顶", data=[target], total=1)
