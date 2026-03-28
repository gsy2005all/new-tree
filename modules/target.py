from sqlmodel import JSON, Column, Field
from datetime import datetime
from modules.base import Base


class Target(Base, table=True):
    name: str = Field(default=None, primary_key=True)
    current_day: int  = Field(default=None)
    deadline: datetime  = Field(default=None)
    days: list[int]  = Field(default=[], sa_column=Column(JSON))
    remind_time: datetime = Field(default=None)
    creater_user: int = Field(default=None)