from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select

from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.day import Day, DayInput
from modules.target import Target
from modules.tree_app_res import TreeAppHttpResponse
from utils.cache import invalidate_prefix

day_router = APIRouter(prefix="/days", dependencies=[Depends(http_log_M), Depends(check_auth_M)])


def check_target_permission(target_id: int, db_handler: DbHandler, request: Request) -> Target:
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(404, "该目标不存在")
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(403, "你没有权限访问该目标的打卡记录")
    return target


@day_router.get("/query/{target_id}", response_model=TreeAppHttpResponse)
def query_days(target_id: int, db_handler: DbHandler, request: Request):
    check_target_permission(target_id, db_handler, request)
    day_list = db_handler.exec(
        select(Day).where(Day.target_id == target_id).order_by(Day.check_date)
    ).all()
    data = list(day_list)
    return TreeAppHttpResponse(message="Days queried successfully", data=data, total=len(data))


@day_router.post("/add/{target_id}", response_model=TreeAppHttpResponse)
def add_day(target_id: int, day_input: DayInput, db_handler: DbHandler, request: Request):
    target = check_target_permission(target_id, db_handler, request)

    # 取消审核机制：所有目标创建后即可直接打卡（不再需要管理员审核通过）

    now = datetime.now()
    if now < target.start_time:
        raise HTTPException(400, "打卡尚未开始")
    if now > target.deadline_time:
        raise HTTPException(400, "已超过截止时间，无法打卡")

    # 打卡日期：允许补打卡（传 check_date），否则取今天
    check_date = day_input.check_date or now.date()

    # 防重复：同一目标同一日期只能打卡一次
    exists = db_handler.exec(
        select(Day).where(Day.target_id == target.id, Day.check_date == check_date)
    ).first()
    if exists:
        raise HTTPException(400, f"{check_date} 当天已打卡，不能重复打卡（如需修改请用更新接口）")

    day_n = Day(day_proof=day_input.day_proof, status=True, check_date=check_date)
    day_n.target_id = target.id

    db_handler.add(day_n)
    # 同步自增 current_day（这是之前遗漏的逻辑）
    target.current_day = (target.current_day or 0) + 1
    db_handler.add(target)

    db_handler.commit()
    db_handler.refresh(day_n)

    invalidate_prefix(f"stats:target:{target.id}:")
    return TreeAppHttpResponse(message="Day added successfully", data=[day_n], total=1)


@day_router.post("/update/{target_id}/{day_id}", response_model=TreeAppHttpResponse)
def update_day(
    target_id: int, day_id: int, day_input: DayInput, db_handler: DbHandler, request: Request
):
    target = check_target_permission(target_id, db_handler, request)
    day = db_handler.get(Day, day_id)
    if not day:
        raise HTTPException(404, "该打卡记录不存在")
    if day.target_id != target.id:
        raise HTTPException(400, "该打卡记录不属于指定目标")

    # 只允许更新证据与（可选）日期，不影响计数
    day.day_proof = day_input.day_proof
    if day_input.check_date is not None:
        day.check_date = day_input.check_date

    db_handler.commit()
    db_handler.refresh(day)

    invalidate_prefix(f"stats:target:{target.id}:")
    return TreeAppHttpResponse(message="Day updated successfully", data=[day], total=1)
