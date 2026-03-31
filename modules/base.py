from typing import Optional

from sqlmodel import  SQLModel , Field
from datetime import datetime


class Base(SQLModel, table=False):
    id:  Optional[int] = Field(default=None, primary_key=True)  #optional表示这个字段可以为None，默认值为None，primary_key=True表示这是主键字段
    created_at: datetime  = Field(default_factory=datetime.utcnow) #default_factory表示默认值由datetime.utcnow函数生成，utcow记录创建时间
    updated_at: datetime  =  Field(default_factory=datetime.utcnow)
    deleted_at: datetime = Field(default_factory=datetime.utcnow)