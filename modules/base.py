from sqlmodel import  SQLModel , Field
from datetime import datetime


class Base(SQLModel, table=False):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime  = Field(default=None)
    updated_at: datetime  =  Field(default=None)
    deleted_at: datetime = Field(default=None)