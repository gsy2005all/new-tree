from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from db.db import DbHandler
from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.user import User, UserInput, UserPayload, UserOutput
from modules.tree_app_res import TreeAppHttpResponse
from utils.jwt import create_jwt
#导入get_passwd_hash函数用于生成密码哈希值
from utils.security import get_passwd_hash, verify_passwd 

# 创建一个APIRouter实例，指定路由的前缀为/users，这样所有在这个路由器中定义的路由都会以/users开头
user_router = APIRouter(prefix="/users", dependencies=[Depends(http_log_M)])

def user_to_user_public(user: User) -> UserOutput:
    # #定义一个函数，将User对象转换为UserPublic对象，返回一个UserPublic对象，包含User对象的name和targets属性
    # return UserPublic(id=user.id, name=user.name, targets=user.targets, created_at=user.created_at, updated_at=user.updated_at, deleted_at=user.deleted_at) 
    #使用字典解包的方式将User对象的属性值传递给UserPublic对象的构造函数，返回一个UserPublic对象，包含User对象的name和targets属性
    return UserOutput(**user.model_dump()) 

# 后端接受到前端发送的JSON数据，需要解析成代码中指定数据类型
# 前端 -> JSON -> 后端 -> Fastapi加工 -> User对象（Python数据类型）

# 后端返回数据给前端，Fastapi会将代码中指定的数据类型转换成JSON格式
# TreeAppHttpResponse对象（Python数据类型） -> Fastapi加工 -> 后端 -> JSON -> 前端

def set_user_token_to_user_public(user: User) -> UserOutput:
    #将User对象转换为UserPublic对象，包含User对象的name和targets属性,UserOutput是返回给前端的用户信息模型类
    user_output = user_to_user_public(user) 
    # 创建一个JWT token，包含用户的id和name等信息
    # 将JWT token设置为UserPublic对象的token属性
    #之所以设置过期时间为7天，是因为这个token是用来保持用户登录状态的，过期时间太短会导致用户频繁登录，过期时间太长又可能存在安全风险
    user_output.token = create_jwt({"user_id": user.id, "user_name": user.name, "role": user.role}, expire_minutes=60*24*7)
    #返回一个UserPublic对象，包含User对象的name和targets属性，以及JWT token
    return user_output 

# 定义一个POST请求的路由，路径为/users/add，响应模型为TreeAppRes
@user_router.post("/add", response_model=TreeAppHttpResponse)   
# 定义一个函数，参数x是一个usercreate对象，db_handler是一个可以操作数据库的对象
def add_user(user_input: UserInput, db_handler: DbHandler):
    found_user = db_handler.exec(select(User).where(User.name  == user_input.name)).first()

    if found_user:
        raise HTTPException(status_code=400, detail="Has same user!")
    
    user_n = User(**user_input.model_dump())

    # 将User对象的password属性设置为哈希密码
    user_n.password = get_passwd_hash(user_n.password) 
    # 将User对象添加到数据库会话中
    db_handler.add(user_n) 
    # 提交数据库会话，将添加的User对象保存到数据库中
    db_handler.commit() 
    # 刷新数据库会话中的User对象，获取数据库中生成的id等字段的值
    db_handler.refresh(user_n) 

    # 返回添加的User对象，包含数据库中生成的id等字段的值
    return TreeAppHttpResponse(message="User added successfully", data=[set_user_token_to_user_public(user_n)], total=1) 

@user_router.post("/login", response_model=TreeAppHttpResponse)
def login_user(user_n: User, db_handler: DbHandler):
    # 查询数据库中是否存在用户名为user_n.name的User对象
    found_user = db_handler.exec(select(User).where(User.name == user_n.name)).first()
    # 如果不存在，返回一个HTTP 404错误，提示用户名或密码无效
    if found_user is None:
        raise HTTPException(status_code=404, detail="The user does not exist") 
    
    # 如果不匹配，返回一个HTTP 400错误，提示用户名或密码无效
    if not verify_passwd(user_n.password, found_user.password): 
        # 如果存在，使用verify_passwd函数验证输入的密码是否与数据库中存储的哈希密码匹配
        raise HTTPException(status_code=400, detail="Invalid username or password") 
    
    # 如果匹配，返回查询到的User对象，表示登录成功
    return TreeAppHttpResponse(message="Login successful", data=[set_user_token_to_user_public(found_user)], total=1) 

# 定义一个POST请求的路由，路径为/users/tokenlogin，响应模型为TreeAppRes，依赖项为check_auth_M函数
@user_router.post("/tokenlogin", response_model=TreeAppHttpResponse, dependencies=[Depends(check_auth_M)])
def token_login(request: Request, db_handler: DbHandler):
    # 从请求状态中获取用户负载信息
    user_payload: UserPayload = request.state.user_payload
    
    # 如果不存在，返回一个HTTP 404错误，提示用户不存在
    if user_payload is None:
        raise HTTPException(status_code=404, detail="The user does not exist") 

    # 从请求状态中查询用户负载信息，获取用户的id和name等信息
    found_user = db_handler.get(User, user_payload.user_id) 
    
    # 如果不存在，返回一个HTTP 404错误，提示用户不存在
    if found_user is None:
        raise HTTPException(status_code=404, detail="The user does not exist") 
    
    user_public = user_to_user_public(found_user)
    user_public.token = request.state.token

    # 如果存在，返回查询到的User对象，表示token登录成功
    return TreeAppHttpResponse(message="Token login successful", data=[user_public], total=1) 