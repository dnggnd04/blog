from pydantic import BaseModel
from typing import Optional

class LikeModel(BaseModel):
    author_id: Optional[int]
    post_id: int

class LikeResponse(BaseModel):
    id: int
    like: int
    

