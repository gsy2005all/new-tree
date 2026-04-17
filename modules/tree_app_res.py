from pydantic import BaseModel
from typing import List
#为了统一API的响应格式，方便前端处理和展示数据
class TreeAppHttpResponse(BaseModel):
    message: str
    #定义一个属性data，类型为list，默认值为一个空列表
    data: List = [] 