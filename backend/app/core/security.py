import jwt
import uuid

from typing import Any, Union
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(user_name: Union[int, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )
    to_encode = {
        "exp": expire,
        "user_name": user_name,
        "type": "access"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        settings.SECURITY_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(user_name: Union[int, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS
    )
    to_encode = {
        "exp": expire,
        "user_name": user_name,
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        settings.SECURITY_ALGORITHM
    )
    return encoded_jwt