from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    deleted_at: Optional[datetime] = Field(default=None)