"""
简单的内存滑动窗口限流。

仅用于敏感接口（登录/注册）防爆破；按客户端 IP 统计。
适合单实例规模；多实例需替换为 Redis 版（接口保持不变即可）。
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request

from utils.config import get_settings

_lock = Lock()
# ip -> deque[timestamp]
_records: defaultdict[str, deque] = defaultdict(deque)


def ratelimit_M(request: Request):
    """依赖函数：超出窗口内最大请求数则拒绝。"""
    s = get_settings()
    client = request.client.host if request.client else "unknown"
    now = time.time()
    window = s.ratelimit_window
    max_n = s.ratelimit_max

    with _lock:
        q = _records[client]
        # 清掉窗口外的旧记录
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= max_n:
            raise HTTPException(
                429, f"请求过于频繁，请 {window} 秒后再试（最多 {max_n} 次）"
            )
        q.append(now)
    return request
