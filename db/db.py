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
    global engine #全局变量
    sqlite_file_name = "database.db" #指定数据库文件的名称
    sqlite_url =f"sqlite:///{sqlite_file_name}" #数据库连接URL，格式为sqlite:///数据库文件路径
    connect_args ={"check_same_thread":False} #SQLite特有的连接参数，允许多个线程访问同一个数据库连接
    engine=create_engine(sqlite_url,connect_args=connect_args) #数据库的操作权
    SQLModel.metadata.create_all(engine) #根据定义的模型类创建数据库表，如果表已经存在则不会重复创建S
    logger.info("The database.db created.")

#fastapi的依赖函数
def get_session(): #获取数据库会话的函数，作为FastAPI的依赖项
    with Session(engine) as session: #创建数据库会话，使用with语句确保会话在使用后正确关闭
        yield session #提供数据库会话给依赖项，使用yield关键字将会话返回给调用者，并在调用者完成后自动关闭会话
      

DbHandler = Annotated[Session, Depends(get_session)] #依赖注入，把获取数据库会话封装成可复用的类型注解