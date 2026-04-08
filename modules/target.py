from sqlmodel import JSON, Column, Field
from datetime import datetime
from modules.base import Base


class Target(Base, table=True):
    name: str = Field(default=None)
    creater_user: int = Field(default=None)  #创建者用户id
    current_day: int  = Field(default=0)
    days: list[int]  = Field(default=[], sa_column=Column(JSON))
    deadline_time: datetime  = Field(default=None)
    remind_time: datetime = Field(default=None) 

class TargetInput(Base):
    name: str
    deadline_time: datetime
    remind_time: datetime