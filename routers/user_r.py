from fastapi import APIRouter
from db.db import SessionDep
from modules.user import User 
from utils.security import get_passwd_hash #导入get_passwd_hash函数用于生成密码哈希值

user_router = APIRouter(prefix="/users")#创建一个APIRouter实例，指定路由的前缀为/users，这样所有在这个路由器中定义的路由都会以/users开头

@user_router.post("/add", response_model=User)   #定义一个POST请求的路由，路径为/users/add，响应模型为User
def add_user(x: User, session: SessionDep):  #定义一个函数，参数x是一个usercreate对象，session是一个数据库会话对象
    x.password = get_passwd_hash(x.password) #生 #将User对象的password属性设置为哈希密码
    session.add(x) #将User对象添加到数据库会话中
    session.commit() #提交数据库会话，将添加的User对象保存到数据库中
    session.refresh(x) #刷新数据库会话中的User对象，获取数据库中生成的id等字段的值
    return x #返回添加的User对象，包含数据库中生成的id等字段的值
