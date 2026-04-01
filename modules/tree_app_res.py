from pydantic import BaseModel
from typing import List

class TreeAppHttpResponse(BaseModel):
    message: str
    data: List = [] #定义一个属性data，类型为list，默认值为一个空列表