import datetime
import os
from zoneinfo import ZoneInfo
import jwt

UTC = ZoneInfo("UTC")
SECRET_KEY = os.getenv("JWT_SECRET")

# 创建JWT
def create_jwt(payload: dict, expire_minutes: int = 30) -> str:
    """创建 JWT（UTC 时间戳，符合规范）"""
    exp = datetime.datetime.now(UTC) + datetime.timedelta(minutes=expire_minutes)
    
    token_payload = {
        **payload,
        "iat": int(datetime.datetime.now(UTC).timestamp()),  # 签发时间
        "exp": int(exp.timestamp()),  # 过期时间（UTC 时间戳）
    }
    
    return jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

# 验证并解码JWT
def decode_jwt(token: str) -> tuple[bool, dict | None]:    
    payload = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False, None
    except jwt.InvalidTokenError:
        return False, None
    return True, payload
    