from fastapi import APIRouter, HTTPException, status, Depends
from models import User
from schemas import UserCreate, UserResponse,Token,Pwdchange,Verifypwd
from security import get_password_hash,verify_password,create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import get_current_user

router = APIRouter(prefix = "/auth",tags= ["认证模块"])

#用户注册
@router.post("/register", response_model= UserResponse)
async def register(user_in: UserCreate):
    user_exist = await User.filter(username = user_in.username).exists()
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被占用"
        )
    
    hashed_password = get_password_hash(user_in.password)

    user_obj = await User.create(
        username = user_in.username,
        password = hashed_password
    )
    return user_obj

#用户登录
@router.post("/login",response_model= Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    #必须加上first()，确保返回的是一个对象，filter返回的是一个对象列表，只有一个对象也是列表
    user = await User.filter(username = form_data.username).first() 
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = create_access_token(data = {"sub" : str(user.id)})  #强制转换user.id为str
    return {"access_token":token , "token_type": "Bearer"}

#修改密码
@router.put("/modify")
async def modify_pwd(pwd: Pwdchange, 
                     current_user = Depends(get_current_user)):
    if not verify_password(pwd.ori_pwd,current_user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "原密码输入错误"
        )
    if not (pwd.ori_pwd == pwd.new_pwd):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "新密码不能和原密码相同"
        )
    current_user.password = get_password_hash(pwd.new_pwd)
    await current_user.save()
    return "修改成功,请重新登录！"

@router.post("/close")
async def close_account(input_pwd: Verifypwd,current_user = Depends(get_current_user)):
    """
    用户注销
    """
    if not verify_password(input_pwd.pwd,current_user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "密码错误！"
        )
    await current_user.delete()
    return "注销成功！"
# 直接返回ORM对象时，Fastapi会自动将对象中的属性提取转换成字典，再转换成Json格式返回
# 如果有response_model过滤，可将过滤后的属性返回        
@router.get("/test", response_model=UserResponse)   #测试用户令牌功能
async def test(current_user = Depends(get_current_user)):
    return current_user
            
        
    