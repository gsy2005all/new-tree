from typing import Optional

from sqlmodel import  SQLModel , Field
from datetime import datetime


class Base(SQLModel, table=False):
    id:  Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime  = Field(default_factory=datetime.utcnow)
    updated_at: datetime  =  Field(default_factory=datetime.utcnow)
    deleted_at: datetime = Field(default_factory=datetime.utcnow)