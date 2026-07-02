from dotenv import load_dotenv

load_dotenv()  # 导入.env文件中的环境变量


from contextlib import asynccontextmanager

from db.db import create_db_and_tables
from routers.admin_r import admin_router
from routers.app_r import app_router
from routers.day_r import day_router
from routers.stats_r import stats_router
from routers.target_r import target_router
from routers.upload_r import upload_router
from routers.user_r import user_router
from utils.config import get_settings, validate_startup
from utils.exceptions import register_exception_handlers
from utils.log import init_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import uvicorn


# 这里是APP生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动自检：必填配置缺失、上传目录可写等
    validate_startup()
    init_logger()
    create_db_and_tables()

    yield  # 这里表示 APP 开始执行的时候

    # 这里是APP生命周期结束要做的事情
    logger.info("The application is shutting down")


# 创建 FastAPI 应用实例，并指定生命周期函数
app = FastAPI(lifespan=lifespan)

# CORS：当前虽同源，但为将来前后端分离预留
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理，统一错误响应格式
register_exception_handlers(app)

# 将各路由器包含到 FastAPI 应用中
app.include_router(user_router)
app.include_router(target_router)
app.include_router(day_router)
app.include_router(stats_router)
app.include_router(upload_router)
app.include_router(app_router)
app.include_router(admin_router)

# 访问根路径 / 时，自动跳转到入口选择页面（手机模拟器首页）
@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")

# 把 static 目录挂载为静态资源，前端页面(手机模拟器)与上传图片都由它提供
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# localhost、127.0.0.1 表示监听本地机器
# 0.0.0.0 表示 监听所有的IP地址（包括本地和外部访问）
# 8000 是监听的端口号，可以根据需要修改
if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
