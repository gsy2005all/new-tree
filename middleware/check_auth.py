from fastapi import HTTPException, Request
from modules.user import UserPayload
from utils.jwt import decode_jwt

# 参数是一个Request对象，用于检查请求中的授权token是否合法，并将解析后的用户负载信息存储在请求状态中,token表示授权token
def check_auth_M(request: Request):
    # 从前端发送的请求中的请求头里面获取 X-Auth-Token , 当然可以任意修改
    token = request.headers.get("X-Auth-Token", None)
    if not token:
        raise HTTPException(status_code=400, detail="前端请求头中未携带授权的token, 拒绝访问!!!")

    is_valid, payload = decode_jwt(token)

    if not is_valid:
        raise HTTPException(status_code=400, detail="授权token无效, 拒绝访问!!!")
    
    if payload is None:
        raise HTTPException(status_code=400, detail="授权token解析失败, 拒绝访问!!!")

    # 将解析后的用户载荷信息存储在请求状态中，供后续的路由处理函数使用
    request.state.user_payload = UserPayload(**payload)
    request.state.token = token

    return request