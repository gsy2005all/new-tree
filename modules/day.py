from sqlmodel import Field
from modules.base import Base


class Day(Base, table=True):#定义一个Day类，继承自Base类，所以没有主键字段
    day_proof: str = Field(default=None)
    status: str = Field(default=None)