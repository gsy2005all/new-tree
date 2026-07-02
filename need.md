# 打卡树功能需求

## 1、功能：
- 登录、注册
- 创建、修改、删除打卡目标
- 打卡、修改证据
- 打卡图片上传（multipart + Pillow 校验/压缩）√
- 连续打卡统计、完成率、打卡日历 √
- 防重复打卡（同目标同日仅一次）√

## 2、数据结构定义
0、Base(共有数据字段)
- id            : int
- created_at    : datetime
- updated_at    : datetime
- deleted_at    : datetime | None

1、User(用户)
- name          : str
- password      : str
- role          : str        user/admin √
- targets       : list[int] 这个用户的目标们的id，用于区分不同用户的不同多个目标

2、Target
- name          : str
- current_day   : int
- start_time    : datetime
- deadline_time : datetime
- remind_time   : datetime
- creater_user  : int
- audit_status  : str        pending/approved/rejected √

3、day
- day_proof     : str 这里存放的是图片的路径(URL)
- check_date    : date  打卡日期（统计/去重用）√

# 3、优化
- 提供读取day_proof图片数据的路由       √ (/uploads/{filename} + /static/uploads 静态托管)
- 将query相关的功能增加分页处理         √
- 实现缓存功能（可以使用中间件处理）      √ (cachetools TTLCache + 写操作主动失效)

