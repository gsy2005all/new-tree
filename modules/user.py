from sqlmodel import Field, Column, JSON
from modules.base import Base


class User(Base, table=True):
    name: str = Field(default=None)
    password: str  = Field(default=None)
    targets: list[int] = Field(default=[], sa_column=Column(JSON))#JSON类型的字段，默认值为一个空列表，sa_column=Column(JSON)表示在数据库中使用JSON类型存储这个字段