# 打卡树功能需求

## 1、功能：
- 登录、注册
- 创建、修改、删除打卡目标
- 打卡

## 2、数据结构定义
0、Base(共有数据字段)
- id            : int
- created_at    : datetime
- updated_at    : datetime
- deleted_at    : datetime | None

1、User(用户)
- name          : str
- password      : str
- total_target  : int
- targets       : list[int] 这个用户的目标们的id，用于区分不同用户的不同多个目标

2、Target
- name          : str
- current_day   : int
- deadline      : datetime
- days          : list[int] 
- remind_time   : datetime
- creater_user  : int

3、day
- day_proof     : str 这里存放的是图片的路径
- status        : bool True=打卡了，False=未打卡