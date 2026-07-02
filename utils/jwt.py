import datetime
from zoneinfo import ZoneInfo

import jwt

from utils.config import get_settings

UTC = ZoneInfo("UTC")


def create_jwt(payload: dict, expire_minutes: int | None = None) -> str:
    """创建 JWT（UTC 时间戳，符合规范）。过期时间默认取配置中的 7 天。"""
    settings = get_settings()
    if expire_minutes is None:
        expire_minutes = settings.jwt_expire_minutes

    now = datetime.datetime.now(UTC)
    exp = now + datetime.timedelta(minutes=expire_minutes)

    token_payload = {
        **payload,
        "iat": int(now.timestamp()),  # 签发时间
        "exp": int(exp.timestamp()),  # 过期时间（UTC 时间戳）
    }
    return jwt.encode(token_payload, settings.jwt_secret, algorithm="HS256")


def decode_jwt(token: str) -> tuple[bool, dict | None]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False, None
    except jwt.InvalidTokenError:
        return False, None
    return True, payload
