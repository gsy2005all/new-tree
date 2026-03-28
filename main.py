from contextlib import asynccontextmanager
from db.db import create_db_and_tables
from utils.log import init_logger
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger
from os import environ
import uvicorn
#这上面的是导入模块和库的部分，下面是导入我们自己写的模块

from modules.user import User
from modules.target import Target
from modules.day import Day

load_dotenv() # 导入.env文件中的环境变量

# 这里是APP生命周期
@asynccontextmanager
async def lifespan(app:FastAPI):
    # 这里是APP生命周期开始要做的事情
    init_logger()
    create_db_and_tables()

    yield#这里表示"你的"APP开始执行的时候
    
    #这里是APP生命周期结束要做的事情
    logger.info("The application is shutting down")
    
# 创建FastAPI应用实例，并指定生命周期函数
app=FastAPI(lifespan=lifespan)

# localhost、127.0.0.1 表示监听本地机器
# 0.0.0.0 表示 监听所有的IP地址（包括本地和外部访问）

# 8000 是监听的端口号，可以根据需要修改
if __name__ == "__main__":
     uvicorn.run(app, host=environ.get("HOST", "0.0.0.0"), port=int(environ.get("PORT", 8000))) 