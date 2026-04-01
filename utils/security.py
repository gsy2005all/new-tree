from passlib.context import CryptContext

#下载了passlib库和bcrypt库，passlib是一个密码哈希库，提供了多种哈希算法的实现，bcrypt是其中一种常用的哈希算法，适用于密码存储和验证。
# 配置密码哈希方式 推荐bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #创建一个密码上下文对象，指定使用bcrypt算法进行密码哈希，并设置过时算法的处理方式为自动

def verify_passwd(plain_passwd: str, hashed_passwd: str) -> bool:
    """验证密码是否正确"""
    return pwd_context.verify(plain_passwd, hashed_passwd)

def get_passwd_hash(passwd: str) -> str:
    """生成密码的哈希值"""
    return pwd_context.hash(passwd)