from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field
from sqlmodel import Column, JSON, Relationship
from modules.base import Base

# 避免循环导入
if TYPE_CHECKING:
    from modules.target import Target

# 用户角色常量：普通用户(用户端) 与 管理员(管理端)
ROLE_USER = "user"
ROLE_ADMIN = "admin"

class User(Base, table=True):
    name: str = Field(default=None)
    # 手机号：手机验证码登录的唯一标识，唯一约束
    phone: str = Field(default=None, unique=True, index=True)
    # 密码：兼容旧账号；手机验证码登录的用户不需要密码
    password: str | None = Field(default=None)
    # 用户角色，默认是普通用户(user)；值为 admin 时拥有管理端审核权限
    role: str = Field(default=ROLE_USER)
    targets: list["Target"] = Relationship(back_populates="creater_user")

# 定义一个名为UserInput的类，继承自Base,UserInput是一个用户输入模型类
class UserInput(BaseModel):
    name: str
    password: str

# 手机验证码登录的输入：手机号 + 验证码
class PhoneLoginInput(BaseModel):
    phone: str
    code: str
    # 昵称（可选，注册时设置）
    name: str | None = None

# 定义一个名为UserPublic的类，继承自Base,UserPublic是一个公共的用户模型类
class UserOutput(BaseModel):
    name: str = Field(default=None)
    phone: str | None = Field(default=None)
    role: str = Field(default=ROLE_USER)
    token: str = Field(default=None)
    targets: list[int] = Field(default=[], sa_column=Column(JSON))

# JWT 负载
class UserPayload(BaseModel):
    user_id: int = Field(default=None)
    user_name: str = Field(default=None)
    phone: str | None = Field(default=None)
    role: str = Field(default=ROLE_USER)
