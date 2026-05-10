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