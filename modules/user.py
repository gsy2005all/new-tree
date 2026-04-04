from sqlmodel import Field, Column, JSON
from modules.base import Base


class User(Base, table=True):
    name: str = Field(default=None)
    password: str  = Field(default=None)
    targets: list[int] = Field(default=[], sa_column=Column(JSON)) #JSON类型的字段，默认值为一个空列表，sa_column=Column(JSON)表示在数据库中使用JSON类型存储这个字段

class UserPublic(Base): #定义一个名为UserPublic的类，继承自Base,UserPublic是一个公共的用户模型类，用于表示用户的公共信息，里面不包含密码等敏感信息
    name: str = Field(default=None)
    token: str = Field(default=None)
    targets: list[int] = Field(default=[], sa_column=Column(JSON))

class UserPayload(Base): #定义一个名为UserPayload的类，继承自Base,UserPayload是一个用户负载模型类，用于表示用户的负载信息，里面包含用户的id、email、name和是否是管理员等信息
    user_id: int = Field(default=None)
    user_name: str = Field(default=None)