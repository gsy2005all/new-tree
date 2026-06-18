from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship
from datetime import datetime
from modules.base import Base
from modules.user import UserOutput

# 避免循环导入
if TYPE_CHECKING:
    from modules.day import Day
    from modules.user import User

# 打卡目标的审核状态常量
AUDIT_PENDING = "pending"      # 待审核（用户刚提交/修改后）
AUDIT_APPROVED = "approved"    # 审核通过（用户才能开始打卡）
AUDIT_REJECTED = "rejected"    # 审核不通过

class Target(Base, table=True):
    name: str = Field(default=None)
    creater_user_id: int | None = Field(default=None, foreign_key="user.id")
    creater_user: Optional["User"] = Relationship(back_populates="targets")
    days: list["Day"] = Relationship(back_populates="target")
    current_day: int  = Field(default=0)
    start_time: datetime = Field(default=None)
    deadline_time: datetime  = Field(default=None)
    remind_time: datetime = Field(default=None)
    # ===== 管理端审核相关字段 =====
    audit_status: str = Field(default=AUDIT_PENDING)      # 审核状态：pending/approved/rejected
    audit_reason: str | None = Field(default=None)        # 审核意见/不通过原因（人工或AI给出）
    audited_by: int | None = Field(default=None)          # 审核人(管理员)的 user_id；AI 自动审核时为 None
    audited_at: datetime | None = Field(default=None)     # 审核时间

#TargetInput是一个目标输入模型类，用于表示目标的输入信息，里面包含目标的name、deadline_time和remind_time等信息
class TargetInput(BaseModel):
    name: str
    start_time: datetime
    deadline_time: datetime
    remind_time: datetime

class TargetUpdateInput(TargetInput):
    update_field: list[str]

# 管理端人工审核的输入：approved=True 表示通过，False 表示驳回；reason 是审核意见
class TargetAuditInput(BaseModel):
    approved: bool
    reason: str | None = None
