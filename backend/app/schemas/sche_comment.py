from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: Optional[str] = None
    post_id: Optional[int] = None
    author_id: Optional[int] = None

    class Config:
        orm_mode = True

class CommentCreateRequest(CommentBase):
    content: str
    post_id: int
    author_id: Optional[int]

class CommentResponse(CommentBase):
    id: int
    content: str
    post_id: int
    author_id: int
    update_at: datetime
    full_name: str
    avatar: str
    type: str

class ChangeMyCommentRequest(BaseModel):
    id: int
    content: str