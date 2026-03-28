# 创建数据库和表
from loguru import logger
from sqlmodel import SQLModel, create_engine


def create_db_and_tables():
    sqlite_file_name = "database.db" #指定数据库文件的名称
    sqlite_url =f"sqlite:///{sqlite_file_name}" 
    connect_args ={"check_same_thread":False}
    engine=create_engine(sqlite_url,connect_args=connect_args)#数据库的操作权
    SQLModel.metadata.create_all(engine)
    logger.info("The database.db created.")