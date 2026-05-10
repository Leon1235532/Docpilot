from fastapi import APIRouter, HTTPException, status, Depends,Query
from models import Document,User
from dependencies import get_current_user
from schemas import DocumentCreate,Page_doc_respond,DocumentOut,DocumentUpdate,DocumentSummary
from ai_service import generate_doc_summary

router = APIRouter(prefix="/docs", tags=["文档管理"])

@router.post("/create" ,response_model= DocumentOut)
async def doc_create(doc_info: DocumentCreate, Current_User: User = Depends(get_current_user)):
    new_doc =await Document.create(
        title = doc_info.title,
        content = doc_info.content,
        User = Current_User
    )
    return new_doc

@router.get("/get_all",response_model = Page_doc_respond)
async def get_doc_all(Current_User: User = Depends(get_current_user),
                      page: int = Query(1, ge= 1, description="页码"),
                      page_size: int = Query(5, le= 100, description="数量")):
    total = await Document.filter(User = Current_User).count()
    total_pages = (total + page_size - 1) // page_size
    skip_pages = (page - 1) * page_size
    doc_obj = await Document.filter(User = Current_User).offset(skip_pages).limit(page_size).all() 
    return {"data":doc_obj,
            "message": f"第{page}页，共{total_pages}页"}

@router.get("/get_single",response_model = DocumentOut)
async def get_doc_single(doc_id: int,Current_User: User = Depends(get_current_user)):
    doc = await Document.get_or_none(id = doc_id, User = Current_User)
    if not doc:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "文件不存在或您无权查看！"
        )
    return doc

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doc(doc_id: int, Current_User: User = Depends(get_current_user)):
    doc = await Document.get_or_none(id = doc_id, User = Current_User)
    if not doc:
        raise HTTPException(
            status_code= status.HTTP_404_UNAUTHORIZED,
            detail = "文件不存在或您无权删除！"
        )
    await doc.delete()
    return

@router.patch("/update", response_model=DocumentOut)
async def updtae_doc(doc_id: int,Update_data: DocumentUpdate,
                     Current_User: User = Depends(get_current_user)):
    doc = await Document.get_or_none(id = doc_id, User = Current_User)
    if not doc:
        raise HTTPException(
            status_code= status.HTTP_404_UNAUTHORIZED,
            detail = "文件不存在或您无权修改！"
        )
    Update_dict = Update_data.model_dump(exclude_unset=True)
    if Update_dict:
        doc.update_from_dict(Update_dict)
        await doc.save()
    return doc    

@router.post("/ai_Summary", response_model = DocumentSummary)
async def get_summary(doc_id: int, Current_User: User = Depends(get_current_user)):
    doc = await Document.filter(id=doc_id, User = Current_User).first()
    if not doc:
        raise HTTPException(status_code=404, detail="找不到该文档或您没有权限")
    try:
        summary_text = await generate_doc_summary(Current_User, doc.content)
        return {"doc_id": doc_id, "summary": summary_text}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务异常: {str(e)}")