from sqlmodel import Field, Column, JSON
from modules.base import Base


class User(Base, table=True):
    name: str  = Field(default=None, primary_key=True)
    password: str  = Field(default=None)
    targets: list[int] = Field(default=[], sa_column=Column(JSON))