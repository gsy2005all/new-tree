"""
打卡统计：连续打卡天数(streak)、完成率、打卡日历、距截止剩余天数等。

这是把一个"能打卡"的应用变成"成熟的打卡应用"的关键信息层，
让用户能看到自己的坚持与进度。
"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select

from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.day import Day
from modules.target import Target
from modules.tree_app_res import TreeAppHttpResponse
from utils.cache import invalidate_prefix

stats_router = APIRouter(prefix="/stats", dependencies=[Depends(http_log_M), Depends(check_auth_M)])


def _calc_streak(check_dates: list[date], today: date) -> int:
    """计算当前连续打卡天数：从今天/昨天往前连续不间断的最大天数。"""
    if not check_dates:
        return 0
    dates = sorted({d for d in check_dates}, reverse=True)  # 倒序、去重
    # 如果最近一次打卡既不是今天也不是昨天，说明已经断卡，streak=0
    if dates[0] != today and dates[0] != today - timedelta(days=1):
        return 0
    streak = 1
    for prev, cur in zip(dates, dates[1:]):
        if prev - cur == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


@stats_router.get("/target/{target_id}", response_model=TreeAppHttpResponse)
def target_stats(target_id: int, db_handler: DbHandler, request: Request):
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(404, "该目标不存在")
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(403, "无权查看该目标的统计")

    today = date.today()
    days = db_handler.exec(
        select(Day).where(Day.target_id == target_id).order_by(Day.check_date)
    ).all()
    check_dates = [d.check_date for d in days if d.check_date is not None]
    total_checked = len(check_dates)

    # 应打卡天数：从 start 到 min(deadline, today)
    start_d = target.start_time.date() if target.start_time else None
    end_d = (target.deadline_time.date() if target.deadline_time else today)
    expected_days = 0
    if start_d and end_d >= start_d:
        expected_days = (min(end_d, today) - start_d).days + 1
        expected_days = max(expected_days, 0)

    completion_rate = round(total_checked / expected_days, 4) if expected_days > 0 else 0.0

    remaining_days = None
    if target.deadline_time:
        remaining_days = (target.deadline_time.date() - today).days
        remaining_days = max(remaining_days, 0)

    streak = _calc_streak(check_dates, today)

    # 打卡日历：便于前端画热力图
    calendar = sorted(d.isoformat() for d in check_dates)

    data = [
        {
            "target_id": target.id,
            "target_name": target.name,
            "current_day": target.current_day,
            "total_checked": total_checked,
            "expected_days": expected_days,
            "completion_rate": completion_rate,
            "streak": streak,
            "remaining_days": remaining_days,
            "audit_status": target.audit_status,
            "calendar": calendar,
        }
    ]
    return TreeAppHttpResponse(message="统计查询成功", data=data, total=1)


# 当 day 发生变动时，day_r 里已主动 invalidate_prefix("stats:target:...")
# 这里用不到装饰器缓存（统计计算本身很轻），保留 invalidate 机制即可。
