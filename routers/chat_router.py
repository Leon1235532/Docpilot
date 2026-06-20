from fastapi import APIRouter,Depends
from schemas import AskRequest
from AI_Services.rag_engine import chat_with_doc
import traceback
from models import User
from dependencies import get_current_user
import json
import redis

router = APIRouter(prefix="/input",tags=["问答模块"])
try:
    r = redis.Redis(host = '127.0.0.1',port = 6379,decode_responses=True)
except Exception as e:
    print(f"Redis 初始化失败，请检查数据库状态: {e}")

@router.post("/ask")
async def chat_with_doc_api(request: AskRequest, Current_User: User = Depends(get_current_user)):
    chat_key = f"chat_cache:{Current_User.id}:{request.doc_id}:{request.question}"
    try:
        cached_response = r.get(chat_key)
        if cached_response:
            print("Redis缓存命中!")
            return{
                "code": 200,
                "message": "success",
                "data": json.loads(cached_response),
                "source": "Redis极速缓存"
            }
        print("Redis缓存未命中!")
    except Exception as e:
        print("Redis读取异常,将调用大模型回答!")

    try:
        # 💡 调用新引擎
        result = await chat_with_doc(
            user_id=Current_User.id,
            doc_id=request.doc_id, # 确保前端传了
            user_question=request.question
        )
    except Exception as e:
        print("\n" + "="*50)
        traceback.print_exc()
        print("="*50 + "\n")
        return {"code": 500, "message": f"AI 思考时发生错误: {str(e)}"}
    
    try:
        r.set(chat_key,json.dumps(result,ensure_ascii=False),ex = 2592000)
        print("大模型回答成功写入Redis")
    except Exception as e:
        print(f"大模型回答已生成,写入Redis失败,错误说明:{e}")
    return{
        "code": 200, 
        "message": "success", 
        "data": result,
        "source": "大模型回答"
    }