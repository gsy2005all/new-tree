from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship
from datetime import datetime
from modules.base import Base
from modules.user import UserOutput

# 避免循环导入
if TYPE_CHECKING:
    from modules.day import Day
    from modules.user import User

class Target(Base, table=True):
    name: str = Field(default=None)
    creater_user_id: int | None = Field(default=None, foreign_key="user.id")
    creater_user: Optional["User"] = Relationship(back_populates="targets")
    days: list["Day"] = Relationship(back_populates="target")
    current_day: int  = Field(default=0)
    deadline_time: datetime  = Field(default=None)
    remind_time: datetime = Field(default=None) 

#TargetInput是一个目标输入模型类，用于表示目标的输入信息，里面包含目标的name、deadline_time和remind_time等信息
class TargetInput(BaseModel):
    name: str
    deadline_time: datetime
    remind_time: datetime
