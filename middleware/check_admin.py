from fastapi import HTTPException, Request
from modules.user import ROLE_ADMIN, UserPayload

# 管理端鉴权中间件：必须在 check_auth_M 之后执行（check_auth_M 已把 user_payload 写入 request.state）
# 作用是校验当前登录用户的角色是否为管理员(admin)，不是则拒绝访问管理端接口
def check_admin_M(request: Request):
    # 从请求状态中取出 check_auth_M 解析好的用户负载信息
    user_payload: UserPayload | None = getattr(request.state, "user_payload", None)
    if user_payload is None:
        raise HTTPException(status_code=401, detail="未认证, 拒绝访问管理端!!!")

    # 角色不是管理员就拒绝
    if user_payload.role != ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限, 拒绝访问管理端!!!")

    return request
