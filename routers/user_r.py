from fastapi import APIRouter, HTTPException
from sqlmodel import select
from db.db import SessionDep
from modules.user import User, UserPublic
from modules.tree_app_res import TreeAppHttpResponse
from utils.security import get_passwd_hash, verify_passwd #导入get_passwd_hash函数用于生成密码哈希值

user_router = APIRouter(prefix="/users")#创建一个APIRouter实例，指定路由的前缀为/users，这样所有在这个路由器中定义的路由都会以/users开头

def user_to_user_public(user: User) -> UserPublic:
    # #定义一个函数，将User对象转换为UserPublic对象，返回一个UserPublic对象，包含User对象的name和targets属性
    # return UserPublic(id=user.id, name=user.name, targets=user.targets, created_at=user.created_at, updated_at=user.updated_at, deleted_at=user.deleted_at) 
    return UserPublic(**user.model_dump()) #使用字典解包的方式将User对象的属性值传递给UserPublic对象的构造函数，返回一个UserPublic对象，包含User对象的name和targets属性

# 后端接受到前端发送的JSON数据，需要解析成代码中指定数据类型
# 前端 -> JSON -> 后端 -> Fastapi加工 -> User对象（Python数据类型）

# 后端返回数据给前端，Fastapi会将代码中指定的数据类型转换成JSON格式
# TreeAppHttpResponse对象（Python数据类型） -> Fastapi加工 -> 后端 -> JSON -> 前端

@user_router.post("/add", response_model=TreeAppHttpResponse)   #定义一个POST请求的路由，路径为/users/add，响应模型为TreeAppRes
def add_user(user_n: User, session: SessionDep):  #定义一个函数，参数x是一个usercreate对象，session是一个数据库会话对象
    user_n.password = get_passwd_hash(user_n.password) #将User对象的password属性设置为哈希密码
    session.add(user_n) #将User对象添加到数据库会话中
    session.commit() #提交数据库会话，将添加的User对象保存到数据库中
    session.refresh(user_n) #刷新数据库会话中的User对象，获取数据库中生成的id等字段的值
    return TreeAppHttpResponse(message="User added successfully", data=[user_to_user_public(user_n)]) #返回添加的User对象，包含数据库中生成的id等字段的值

@user_router.post("/login", response_model=TreeAppHttpResponse)
def login_user(user_n: User, session: SessionDep):
    found_user = session.exec(select(User).where(User.name == user_n.name)).one_or_none() #查询数据库中是否存在用户名为user_n.name的User对象
    
    if found_user is None:
        raise HTTPException(status_code=404, detail="The user does not exist") #如果不存在，返回一个HTTP 404错误，提示用户名或密码无效
    
    if not verify_passwd(user_n.password, found_user.password): #如果存在，使用verify_passwd函数验证输入的密码是否与数据库中存储的哈希密码匹配
        raise HTTPException(status_code=400, detail="Invalid username or password") #如果不匹配，返回一个HTTP 400错误，提示用户名或密码无效
    
    return TreeAppHttpResponse(message="Login successful", data=[user_to_user_public(found_user)]) #如果匹配，返回查询到的User对象，表示登录成功