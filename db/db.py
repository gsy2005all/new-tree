# 创建数据库和表
from typing import Annotated

from fastapi import Depends
from loguru import logger
from sqlmodel import Session, SQLModel, create_engine

# 这上面的是导入模块和库的部分，下面是导入我们自己写的模块
from modules.day import Day
from modules.target import Target
from modules.user import User
from utils.config import get_settings

# 全局 engine，由 create_db_and_tables() 初始化
engine = None


def create_db_and_tables():
    """根据配置创建数据库引擎与所有表。"""
    global engine
    settings = get_settings()
    # SQLite 特有参数：允许多个线程复用同一连接
    connect_args = {"check_same_thread": False}
    engine = create_engine(settings.sqlite_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    logger.info(f"Database ready at {settings.db_file}")


def get_session():
    """FastAPI 依赖：提供一个数据库会话，用完自动关闭。"""
    with Session(engine) as session:
        yield session


# 依赖注入：把 get_session 封装成可复用的类型注解
DbHandler = Annotated[Session, Depends(get_session)]
