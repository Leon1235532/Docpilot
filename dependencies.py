from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import JWTError, jwt
from models import User
from security import SECRET_KEY, ALGORITHM

'''
HTTPBearer模型:
创建HTTPBearer实例,会自动在页面生成Authorize授权入口,
会自动在 Header 里的 Authorization 找 Bearer Token
'''
Http_scheme = HTTPBearer()  
#从获取的token中解码获得用户信息，查询信息，存在则返回信息
async def get_current_user(credential: HTTPAuthorizationCredentials = Depends(Http_scheme)):    #返回抓取的装有token的对象
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credential.credentials
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)    # 解码得到to_encode字典，存着sub和exp
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    #查询用户对象，若存在则返回
    user = await User.filter(id = user_id).first()
    if user is None:
        raise credentials_exception
    return user
    
