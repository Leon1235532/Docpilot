from pydantic import BaseModel,Field
from datetime import datetime
from typing import List
 
class UserCreate(BaseModel):
    username: str = Field(..., min_length =3, max_length=11)
    password: str = Field(..., min_length =6, max_length=13)

class UserResponse(BaseModel):
    id :int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Pwdchange(BaseModel):
    ori_pwd: str =Field(...,max_length=13)
    new_pwd: str =Field(...,max_length=13)

class Verifypwd(BaseModel):
    pwd : str = Field(...,max_length=13)

class DocumentCreate(BaseModel):
    title: str = Field(...)
    content: str | None = None

class DocumentOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    User_id: int
    class Config:
        from_attributes = True

class Page_doc_respond(BaseModel):
    data: List[DocumentOut]
    message: str

class DocumentUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class DocumentSummary(BaseModel):
    doc_id: int
    summary: str
    source: str

class Response_Limit(BaseModel):
    core_conclusion: str = Field(description="一句话直接回答用户的核心问题或解释核心概念")
    key_details: List[str] = Field(description="详细的知识点解析、步骤、临床表现或核心特征")
    warnings_or_notes: List[str] = Field(description="相关的注意事项、高危提示、预防措施或补充说明（如果没有则输出['无特殊注意事项']）")

class AskRequest(BaseModel):
    question: str = Field(..., description="用户提出的问题")
    doc_id: int = Field(..., description="当前对话关联的专科文献ID")