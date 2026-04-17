from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
from sqlmodel import Field, Relationship
from modules.base import Base

if TYPE_CHECKING:
    from modules.target import Target

class Day(Base, table=True):
    day_proof: str | None = Field(default=None)
    status: bool | None = Field(default=None)
    target_id: int | None = Field(default=None, foreign_key="target.id")
    target: Optional["Target"] = Relationship(back_populates="days")

class DayInput(BaseModel):
    day_proof: str
    