from datetime import date
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship

from modules.base import Base

if TYPE_CHECKING:
    from modules.target import Target


class Day(Base, table=True):
    # 打卡图片的访问路径/URL（由上传接口返回）
    day_proof: str | None = Field(default=None)
    # 打卡状态：True=已打卡；保留 bool 以兼容旧数据
    status: bool | None = Field(default=None)
    target_id: int | None = Field(default=None, foreign_key="target.id")
    target: Optional["Target"] = Relationship(back_populates="days")
    # 打卡日期（本地日期），用于按天统计、去重与计算连续天数
    check_date: date | None = Field(default=None, index=True)


class DayInput(BaseModel):
    day_proof: str
    # 可选手动指定打卡日期；不传则用今天（用于补打卡场景，可被业务规则限制）
    check_date: date | None = None
