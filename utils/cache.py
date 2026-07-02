"""
轻量进程内缓存（基于 cachetools.TTLCache）。

设计：
- cached(ttl, key) 装饰器：缓存函数返回值，按 key 函数生成的键存取。
- 主动失效：invalidate(prefix) 清掉某前缀的所有缓存；写操作（增删改）后调用。
- key 函数约定：把可变参数拼成字符串作为缓存键。

适合当前单体应用规模；后续若多实例部署，再换成 Redis，调用方接口保持不变。
"""
import functools
from threading import Lock

from cachetools import TTLCache

from utils.config import get_settings

_lock = Lock()
_cache: TTLCache | None = None


def _get_cache() -> TTLCache:
    global _cache
    if _cache is None:
        s = get_settings()
        _cache = TTLCache(maxsize=s.cache_maxsize, ttl=s.cache_ttl)
    return _cache


def cached(ttl: int | None = None, key=None):
    """缓存装饰器。

    ttl: 单条缓存存活秒数，None 用全局配置。
    key: 计算缓存键的可调用对象，接收原函数同样的参数，返回字符串。
         默认用 模块名.函数名 + 参数 repr。
    """
    s = get_settings()
    if ttl is None:
        ttl = s.cache_ttl

    def decorator(func):
        default_key = lambda *a, **kw: (
            f"{func.__module__}.{func.__name__}:{a!r}:{sorted(kw.items())!r}"
        )
        key_fn = key or default_key

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = _get_cache()
            k = key_fn(*args, **kwargs)
            with _lock:
                if k in cache:
                    return cache[k]
            result = func(*args, **kwargs)
            with _lock:
                cache[k] = result
            return result

        # 暴露给外部用于主动失效
        wrapper._key_fn = key_fn
        return wrapper

    return decorator


def invalidate_prefix(prefix: str):
    """清掉所有以 prefix 开头的缓存键。"""
    with _lock:
        cache = _get_cache()
        # 复制 keys 避免迭代时修改
        for k in list(cache.keys()):
            if isinstance(k, str) and k.startswith(prefix):
                del cache[k]


def clear_all():
    """清空全部缓存。"""
    with _lock:
        _get_cache().clear()
