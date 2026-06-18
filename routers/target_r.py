from fastapi import APIRouter, Depends, HTTPException, Request, Query
#HTTPException是FastAPI中用于抛出HTTP异常的类，Request是FastAPI中表示HTTP请求的类
from sqlmodel import select
from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.target import Target, TargetInput, TargetUpdateInput, AUDIT_PENDING
from modules.tree_app_res import TreeAppHttpResponse

# 创建一个APIRouter实例，指定路由的前缀为/targets，这样所有在这个路由器中定义的路由都会以/targets开头，并且依赖于http_log_M和check_auth_M中间件函数
target_router = APIRouter(prefix="/targets", dependencies=[Depends(http_log_M), Depends(check_auth_M)])

@target_router.post("/add", response_model=TreeAppHttpResponse)
def add_target(target_input: TargetInput, db_handler: DbHandler, request: Request):
    #创建一个Target对象，使用TargetInput对象的属性值来初始化Target对象的属性值
    target_n = Target(**target_input.model_dump())
    target_n.creater_user_id = request.state.user_payload.user_id

    if target_n.remind_time >= target_n.deadline_time:
        raise HTTPException(400, "Remind time must be before deadline time")
    
    if target_n.start_time >= target_n.deadline_time:
        raise HTTPException(400, "Start time must be before deadline time")
    
    # 将Target对象添加到数据库会话中
    db_handler.add(target_n)
    # 提交数据库会话，将添加的Target对象保存到数据库中
    db_handler.commit()
    # 刷新数据库会话中的Target对象，获取数据库中生成的id等字段的值
    db_handler.refresh(target_n)
    
    # 返回添加的Target对象，包含数据库中生成的id等字段的值
    return TreeAppHttpResponse(message="Target added successfully", data=[target_n], total=1)

# 定义一个GET请求的路由，路径为/targets/query，响应模型为TreeAppRes
@target_router.get("/query", response_model=TreeAppHttpResponse)
    #查询数据库中creater_user_id等于当前用户id的Target对象列表
def query_targets(db_handler: DbHandler, request: Request, offset: int, limit: int = Query(default=100, le=100)):
    #查询数据库中creater_user_id等于当前用户id的Target对象列表，并将结果赋值给target_list变量
    target_list = db_handler.exec(select(Target).where(Target.creater_user_id == request.state.user_payload.user_id).offset(offset).limit(limit).order_by()).all()
    target_total = len(db_handler.exec(select(Target, Target.id).where(Target.creater_user_id == request.state.user_payload.user_id)).all())

    return TreeAppHttpResponse(message="Targets queried successfully", data=list(target_list), total=int(target_total))

# 定义一个POST请求的路由，路径为/targets/update/{target_id}，响应模型为TreeAppResponse
@target_router.post("/update/{target_id}", response_model=TreeAppHttpResponse)
def update_target(target_id: int, target_update_input: TargetUpdateInput, db_handler: DbHandler, request: Request):
    # 查询要修改的Target对象
    target = db_handler.exec(select(Target).where(Target.id == target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    # 检查当前用户是否有权限修改该Target对象
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # 更新Target对象的属性
    for key, value in target_update_input.model_dump().items():
        if key in target_update_input.update_field:
            setattr(target, key, value)

    # 目标内容被修改后需要重新审核，因此重置审核状态为待审核并清空上一次审核结果
    target.audit_status = AUDIT_PENDING
    target.audit_reason = None
    target.audited_by = None
    target.audited_at = None

    # 提交数据库会话，将修改后的Target对象保存到数据库中
    db_handler.commit()
    # 刷新数据库会话中的Target对象，获取更新后的字段的值
    db_handler.refresh(target)

    # 返回修改后的Target对象
    return TreeAppHttpResponse(message="Target updated successfully", data=[target], total=1)

# 定义一个POST请求的路由，路径为/targets/delete/{target_id}，响应模型为TreeAppRes
@target_router.post("/delete/{target_id}", response_model=TreeAppHttpResponse)
def delete_target(target_id: int, db_handler: DbHandler, request: Request):
    # 查询要删除的Target对象
    target = db_handler.exec(select(Target).where(Target.id == target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    # 检查当前用户是否有权限删除该Target对象
    if target.creater_user_id != request.state.user_payload.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # 删除Target对象
    db_handler.delete(target)
    # 提交数据库会话，将删除操作保存到数据库中
    db_handler.commit()

    # 返回删除成功的消息
    return TreeAppHttpResponse(message="Target deleted successfully", data=[target], total=1)
