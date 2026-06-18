from datetime import datetime

from fastapi import APIRouter,Depends, HTTPException, Request
from sqlmodel import select
from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.day import Day, DayInput
from modules.target import Target, AUDIT_APPROVED
from modules.tree_app_res import TreeAppHttpResponse

day_router = APIRouter(prefix="/days", dependencies=[Depends(http_log_M), Depends(check_auth_M)])

def check_target_permission(target_id: int, db_handler: DbHandler, request: Request):
    target = db_handler.get(Target, target_id)
    if not target:
        raise HTTPException(404, "The target does not exist")
    
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(403, "You do not have permission to access this target's days")
    
    return target

@day_router.get("/query/{target_id}", response_model=TreeAppHttpResponse)
def query_days(target_id: int ,db_handler: DbHandler, request: Request):
    check_target_permission(target_id, db_handler, request)

    day_list = db_handler.exec(select(Day).where(Day.target_id == target_id)).all()    

    return TreeAppHttpResponse(message="Days queried successfully", data=list(day_list), total=len(list(day_list)))


@day_router.post("/add/{target_id}", response_model=TreeAppHttpResponse)
def add_day(target_id: int, day_input: DayInput, db_handler: DbHandler, request: Request): 
    target = check_target_permission(target_id, db_handler, request)

    # 只有通过管理端审核(approved)的目标才允许打卡
    if target.audit_status != AUDIT_APPROVED:
        raise HTTPException(403, "The target has not been approved by admin yet")

    if datetime.now() < target.start_time:
        raise HTTPException(400, "The target has not started yet")
    
    if datetime.now() > target.deadline_time:
        raise HTTPException(400, "The target has already passed the deadline")
    
    day_n = Day(**day_input.model_dump())
    day_n.status = True
    day_n.target_id = target.id

    db_handler.add(day_n)
    db_handler.commit()
    db_handler.refresh(day_n)

    return TreeAppHttpResponse(message="Day added successfully", data=[day_n], total=1)

@day_router.post("/update/{target_id}/{day_id}", response_model=TreeAppHttpResponse)
def update_day(target_id: int, day_id: int, day_input: DayInput, db_handler: DbHandler, request: Request):
    target = check_target_permission(target_id, db_handler, request)
    day = db_handler.exec(select(Day).where(Day.id == day_id)).first() 
    if not day:
        raise HTTPException(404, detail="The day does not found")
    
    if day.target_id != target.id:
        raise HTTPException(400, "The day does not belong to the specified target")
    
    for key, value in day_input.model_dump().items():
        setattr(day, key, value)

    db_handler.commit()
    db_handler.refresh(day)
    
    return TreeAppHttpResponse(message="Day updated successfully", data=[day], total=1)
    