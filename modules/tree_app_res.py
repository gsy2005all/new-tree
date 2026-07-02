from typing import Any, List

from pydantic import BaseModel, Field

# 为了统一 API 的响应格式，方便前端处理和展示数据。
# 所有路由都返回这个结构：{ message, data, total }
class TreeAppHttpResponse(BaseModel):
    message: str
    # 用 default_factory 避免可变默认值共享的陷阱
    data: List[Any] = Field(default_factory=list)
    total: int = 0
