from pydantic import BaseModel
from typing import Optional

class PostRequest(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    like_count: int
    full_name: str
    avatar: str

    class Config:
        orm_mode = True

class UpdateMyPostRequest(BaseModel):
    title: Optional[str]
    content: Optional[str]

class UpdatePostRequest(BaseModel):
    title: Optional[str]
    content: Optional[str]
    author_id: Optional[int]