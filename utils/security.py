import bcrypt

def verify_passwd(plain_passwd: str, hashed_passwd: str) -> bool:
    """验证密码是否正确"""
    return bcrypt.checkpw(plain_passwd.encode('utf-8'), hashed_passwd.encode('utf-8'))

def get_passwd_hash(passwd: str) -> str:
    """生成密码的哈希值"""
    return bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')