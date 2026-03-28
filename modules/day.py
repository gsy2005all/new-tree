from sqlmodel import Field
from modules.base import Base


class Day(Base, table=True):
    day_proof: str = Field(default=None, primary_key=True)
    status: str = Field(default=None)