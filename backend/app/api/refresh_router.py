from exceptiongroup import catch
from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.exceptions import HTTPException
from app.schemas.sche_base import DataResponse
from app.schemas.sche_token import Token
from app.services.srv_user import UserService
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token

import jwt


router = APIRouter()

@router.post('', response_model=DataResponse[Token])
async def refresh_token(
    response: Response,
    request: Request,
    user_service: UserService = Depends()
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired refresh token"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_name = payload.get("user_name")
    jti = payload.get("jti")
    
    user_service.verify_refresh_token(user_name, jti)

    new_access_token = create_access_token(user_name)
    new_refresh_token = create_refresh_token(user_name)

    user_service.rotate_refresh_token(user_name, jti, new_refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS
    )

    return DataResponse().success_response(
        {
            "access_token": new_access_token
        }
    )


