from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt
from passlib.context import CryptContext

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 有效期 1 天

def get_password_hash(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

'''
to_encode 存储用户信息:
    一般为"sub": user.id,    # 用户id(告诉系统你是谁) 
    "exp": 过期时间      #多久后失效
'''
def create_access_token(data: dict):
    to_encode = data.copy()    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update( {"exp":expire} )
    return jwt.encode(to_encode,SECRET_KEY,ALGORITHM)   
'''
把用户信息(to_encode)+ 密钥(SECRET_KEY)+ 算法(HS256)
混合加密，生成一串加密字符串

SECRET_KEY为自定义密钥
ALGORITHM为加密算法
'''