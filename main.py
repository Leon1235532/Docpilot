from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from typing import Dict
from routers import auth,docs

api = FastAPI(swagger_ui_parameters={"persistAuthorization": True})
api.include_router(auth.router)
api.include_router(docs.router)

TORTOISE_ORM : Dict = {
    "connections" :{
        "default": "mysql://root:123456@localhost:3306/docpilot",
    },
    "apps":{
        "models": {
            "models": ["models","aerich.models"],  # 模型模块和 Aerich 迁移模型
            "default_connection": "default",
        }
    },

    "use_tz": False,  # 是否使用时区
    "timezone": "UTC",  # 默认时区
    "db_pool": {
        "max_size": 10,  # 最大连接数
        "min_size": 1,   # 最小连接数
        "idle_timeout": 30  # 空闲连接超时（秒）    
    }  

}

register_tortoise(
    app = api,
    config = TORTOISE_ORM,
    generate_schemas=True,  # 开发环境自动生成表结构
    add_exception_handlers=True,  # 添加默认异常处理器
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:api',host = "127.0.0.1",port = 8000,reload = True)