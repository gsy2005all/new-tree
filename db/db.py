# 创建数据库和表
from typing import Annotated

from fastapi import Depends
from loguru import logger
from sqlmodel import SQLModel, Session, create_engine
#这上面的是导入模块和库的部分，下面是导入我们自己写的模块

from modules.user import User
from modules.target import Target
from modules.day import Day

def create_db_and_tables():
    global engine
    sqlite_file_name = "database.db" #指定数据库文件的名称
    sqlite_url =f"sqlite:///{sqlite_file_name}" 
    connect_args ={"check_same_thread":False}
    engine=create_engine(sqlite_url,connect_args=connect_args) #数据库的操作权
    SQLModel.metadata.create_all(engine)
    logger.info("The database.db created.")

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]