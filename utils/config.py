"""
统一的应用配置：用 pydantic-settings 从环境变量 / .env 读取。

好处：
1) 所有配置项有类型、有默认值、有文档，散落在各处的 os.getenv 全部收敛到这里。
2) 启动时即校验（必填项缺失直接报错），避免运行期才发现配置不对。
3) .env 文件由 main.py 顶部 load_dotenv() 加载，这里只负责读取。
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录（main.py 在根目录运行）
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # .env 里多出的字段不报错
    )

    # ===== 服务 =====
    host: str = "0.0.0.0"
    port: int = 8000
    version: str = "0.1.0"

    # ===== 安全 =====
    # JWT 密钥：生产环境必须通过环境变量覆盖；为空时启动会直接报错（见 validate_startup）
    jwt_secret: str = ""
    jwt_expire_minutes: int = 60 * 24 * 7  # 默认 7 天

    # ===== 数据库 =====
    db_file: str = "database.db"

    # ===== 上传 =====
    upload_dir: str = "static/uploads"
    # 允许的图片 MIME 类型
    upload_allowed_types: tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")
    upload_max_bytes: int = 5 * 1024 * 1024  # 5MB

    # ===== 缓存 =====
    cache_ttl: int = 60          # 秒
    cache_maxsize: int = 512

    # ===== 限流 =====
    ratelimit_window: int = 60   # 窗口大小（秒）
    ratelimit_max: int = 10      # 窗口内最大请求数（针对登录/注册等敏感接口）

    # ===== CORS =====
    cors_origins: tuple[str, ...] = ("*",)

    # ===== 日志 =====
    log_format: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"

    @property
    def upload_path(self) -> Path:
        p = Path(self.upload_dir)
        if not p.is_absolute():
            p = BASE_DIR / p
        return p

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.db_file}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_startup():
    """启动自检：关键配置缺失直接抛错，Fail Fast。"""
    s = get_settings()
    if not s.jwt_secret:
        raise RuntimeError(
            "未配置 JWT_SECRET！请在 .env 或环境变量中设置一个足够长的随机字符串。"
        )
    s.upload_path.mkdir(parents=True, exist_ok=True)
