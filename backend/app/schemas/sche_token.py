from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenPayload(BaseModel):
    user_name: Optional[str] = None