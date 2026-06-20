from fastapi import APIRouter, UploadFile, File, Depends
from models import User
from dependencies import get_current_user
import os
import shutil
from AI_Services.rag_engine import process_and_store_pdf

# 实例化一个路由器
router = APIRouter(prefix= "/input",tags=["上传知识库"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...),Current_User: User = Depends(get_current_user)):
    """
    接收前端上传的 PDF 文件接口
    """
    # 坑点预警：PyPDFLoader 只能读取硬盘上的真实文件。
    # 所以我们需要先把前端传过来的内存文件，临时存到本地硬盘上。
    temp_dir = "./User_input_data"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)  # 拼接路径名,自动带分隔符
    
    # 1. 把上传的文件写入临时文件夹
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        chunks_count = process_and_store_pdf(temp_file_path, file.filename)
        # 3. 干完活后，把临时 PDF 文件删掉，保持服务器干净
        os.remove(temp_file_path)
        # 4. 给前端返回成功响应的 JSON
        return {
            "code": 200,
            "message": f"文档 '{file.filename}' 处理成功！",
            "chunks_saved": chunks_count
        }
    except Exception as e:
        return {"code": 500, "message": f"处理失败: {str(e)}"}