import random
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select

from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.user import (
    User, UserInput, UserPayload, UserOutput, PhoneLoginInput, ROLE_USER,
)
from modules.tree_app_res import TreeAppHttpResponse
from utils.jwt import create_jwt
from utils.ratelimit import ratelimit_M
from loguru import logger
from utils.security import get_passwd_hash, verify_passwd

# 创建一个 APIRouter 实例，前缀 /users
user_router = APIRouter(prefix="/users", dependencies=[Depends(http_log_M)])

# ===== 内存验证码存储：phone -> (code, expire_ts)。开发期模拟短信 =====
import time
_code_store: dict[str, tuple[str, float]] = {}
CODE_TTL = 300  # 验证码 5 分钟有效

# 简易手机号格式校验（中国大陆 11 位）
def _valid_phone(p: str) -> bool:
    return bool(re.fullmatch(r"1[3-9]\d{9}", p or ""))


def user_to_user_public(user: User) -> UserOutput:
    return UserOutput(**user.model_dump())


def set_user_token_to_user_public(user: User) -> UserOutput:
    user_output = user_to_user_public(user)
    user_output.token = create_jwt({
        "user_id": user.id,
        "user_name": user.name,
        "phone": user.phone,
        "role": user.role,
    })
    return user_output


# ===== 旧的账号密码注册/登录（保留兼容，管理端仍可用） =====
@user_router.post("/add", response_model=TreeAppHttpResponse, dependencies=[Depends(ratelimit_M)])
def add_user(user_input: UserInput, db_handler: DbHandler):
    found_user = db_handler.exec(select(User).where(User.name == user_input.name)).first()
    if found_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user_n = User(**user_input.model_dump())
    user_n.password = get_passwd_hash(user_n.password)
    db_handler.add(user_n)
    db_handler.commit()
    db_handler.refresh(user_n)
    return TreeAppHttpResponse(message="注册成功", data=[set_user_token_to_user_public(user_n)], total=1)


@user_router.post("/login", response_model=TreeAppHttpResponse, dependencies=[Depends(ratelimit_M)])
def login_user(user_n: User, db_handler: DbHandler):
    found_user = db_handler.exec(select(User).where(User.name == user_n.name)).first()
    if found_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not found_user.password or not verify_passwd(user_n.password, found_user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return TreeAppHttpResponse(message="登录成功", data=[set_user_token_to_user_public(found_user)], total=1)


@user_router.post("/tokenlogin", response_model=TreeAppHttpResponse, dependencies=[Depends(check_auth_M)])
def token_login(request: Request, db_handler: DbHandler):
    user_payload: UserPayload = request.state.user_payload
    found_user = db_handler.get(User, user_payload.user_id)
    if found_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user_public = user_to_user_public(found_user)
    user_public.token = request.state.token
    return TreeAppHttpResponse(message="Token 登录成功", data=[user_public], total=1)


# ===== 手机验证码登录流程（新版主登录方式） =====

@user_router.post("/send-code", response_model=TreeAppHttpResponse, dependencies=[Depends(ratelimit_M)])
def send_code(body: dict):
    """发送验证码。开发期为模拟短信：验证码打印到后端日志，并返回在响应里方便前端展示。"""
    phone = (body.get("phone") or "").strip()
    if not _valid_phone(phone):
        raise HTTPException(400, "手机号格式不正确")
    code = f"{random.randint(0, 999999):06d}"
    _code_store[phone] = (code, time.time() + CODE_TTL)
    # ⚠️ 模拟短信：真实环境这里调用三方 SMS，绝不返回 code 给前端
    logger.info(f"[模拟短信] 发送验证码到 {phone}：{code}")
    return TreeAppHttpResponse(
        message="验证码已发送（模拟）",
        data=[{"phone": phone, "code": code, "ttl": CODE_TTL}],
        total=1,
    )


@user_router.post("/phone-login", response_model=TreeAppHttpResponse, dependencies=[Depends(ratelimit_M)])
def phone_login(body: PhoneLoginInput, db_handler: DbHandler):
    """手机号 + 验证码登录。未注册则自动注册（免密）。"""
    if not _valid_phone(body.phone):
        raise HTTPException(400, "手机号格式不正确")

    # 校验验证码
    rec = _code_store.get(body.phone)
    if not rec:
        raise HTTPException(400, "请先获取验证码")
    code, expire = rec
    if time.time() > expire:
        _code_store.pop(body.phone, None)
        raise HTTPException(400, "验证码已过期，请重新获取")
    if code != body.code:
        raise HTTPException(400, "验证码错误")
    _code_store.pop(body.phone, None)  # 用完即焚

    # 查找或创建用户
    user = db_handler.exec(select(User).where(User.phone == body.phone)).first()
    if user is None:
        # 手机验证码注册：给一个随机不可登录的占位密码，兼容旧表 password NOT NULL 约束
        import secrets as _secrets
        user = User(
            phone=body.phone,
            name=body.name or f"用户{body.phone[-4:]}",
            password=get_passwd_hash("sms_" + _secrets.token_hex(16)),
            role=ROLE_USER,
        )
        db_handler.add(user)
        db_handler.commit()
        db_handler.refresh(user)
        msg = "注册并登录成功"
    else:
        msg = "登录成功"

    return TreeAppHttpResponse(message=msg, data=[set_user_token_to_user_public(user)], total=1)
