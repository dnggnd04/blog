from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    full_name: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False

    class Config:
        orm_mode = True

class UserItemResponse(UserBase):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    is_admin: str
    avatar: str

class UserCreateRequest(UserBase):
    full_name: str
    user_name: str
    email: EmailStr
    password: str
    is_admin: bool = False

class UserRegisterRequest(BaseModel):
    full_name: str
    user_name: str
    email: EmailStr
    password: str
    is_admin: bool = False

class LoginRequest(BaseModel):
    user_name: str
    password: str

class UserChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserUpdateMeRequest(BaseModel):
    full_name: Optional[str]

class UserUpdateRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False