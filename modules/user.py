from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import Field, Column, JSON, Relationship
from modules.base import Base

# 避免循环导入
if TYPE_CHECKING:
    from modules.target import Target

# 用户角色常量：普通用户(用户端) 与 管理员(管理端)
ROLE_USER = "user"
ROLE_ADMIN = "admin"

class User(Base, table=True):
    name: str = Field(default=None, unique=True)
    password: str  = Field(default=None)
    # 用户角色，默认是普通用户(user)；值为 admin 时拥有管理端审核权限
    role: str = Field(default=ROLE_USER)
    targets: list["Target"] = Relationship(back_populates="creater_user")

#定义一个名为UserInput的类，继承自Base,UserInput是一个用户输入模型类，用于表示用户的输入信息，里面包含用户的name和password等信息
class UserInput(BaseModel): 
    name: str
    password: str

#定义一个名为UserPublic的类，继承自Base,UserPublic是一个公共的用户模型类，用于表示用户的公共信息，里面不包含密码等敏感信息
class UserOutput(BaseModel):
    name: str = Field(default=None)
    role: str = Field(default=ROLE_USER)
    token: str = Field(default=None)
    targets: list[int] = Field(default=[], sa_column=Column(JSON))

#定义一个名为UserPayload的类，继承自Base,UserPayload是一个用户负载模型类，用于表示用户的负载信息，里面包含用户的id、email、name和是否是管理员等信息
class UserPayload(BaseModel):
    user_id: int = Field(default=None)
    user_name: str = Field(default=None)
    # 把角色写进 JWT 负载，管理端中间件无需再查数据库即可鉴权
    role: str = Field(default=ROLE_USER)
