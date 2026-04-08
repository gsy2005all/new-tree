from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from db.db import DbHandelr
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.target import Target, TargetInput
from modules.tree_app_res import TreeAppHttpResponse
from utils.jwt import create_jwt
from utils.security import get_passwd_hash, verify_passwd 

# 创建一个APIRouter实例，指定路由的前缀为/targets，这样所有在这个路由器中定义的路由都会以/targets开头，并且依赖于http_log_M和check_auth_M中间件函数
target_router = APIRouter(prefix="/targets", dependencies=[Depends(http_log_M), Depends(check_auth_M)])

@target_router.post("/add", response_model=TreeAppHttpResponse)
def add_target(target_input: TargetInput, db_handelr: DbHandelr, request: Request):
    target_n = Target(**target_input.model_dump())
    target_n.creater_user = request.state.user_payload.user_id

    # 将Target对象添加到数据库会话中
    db_handelr.add(target_n)
    # 提交数据库会话，将添加的Target对象保存到数据库中
    db_handelr.commit() 
    # 刷新数据库会话中的Target对象，获取数据库中生成的id等字段的值
    db_handelr.refresh(target_n) 

    # 返回添加的Target对象，包含数据库中生成的id等字段的值
    return TreeAppHttpResponse(message="Target added successfully", data=[target_n])
