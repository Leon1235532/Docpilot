from fastapi import APIRouter,Depends
from schemas import AskRequest
from AI_Services.rag_engine import chat_with_doc
import traceback
from models import User
from dependencies import get_current_user

router = APIRouter(prefix="/input",tags=["问答模块"])

@router.post("/ask")
async def chat_with_doc_api(request: AskRequest, Current_User: User = Depends(get_current_user)):
    try:
        # 💡 调用新引擎
        result = await chat_with_doc(
            user_id=Current_User.id,
            doc_id=request.doc_id, # 确保前端传了
            user_question=request.question
        )

        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        print("\n" + "="*50)
        traceback.print_exc()
        print("="*50 + "\n")
        return {"code": 500, "message": f"AI 思考时发生错误: {str(e)}"}