from fastapi import APIRouter, Depends, status, WebSocket, Response
from fastapi.exceptions import HTTPException

from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import LoginRequest
from app.schemas.sche_token import Token
from app.services.srv_user import UserService
from app.core.security import create_access_token, create_refresh_token

router = APIRouter()

@router.post('', response_model=DataResponse[Token])
async def login(
    response: Response,
    login_data: LoginRequest,
    user_service: UserService = Depends()
):
    user = user_service.authenticate(user_name=login_data.user_name, password=login_data.password)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    access_token = create_access_token(user.user_name)
    refresh_token = create_refresh_token(user.user_name)

    user_service.save_refresh_token(user, refresh_token)

    response.set_cookie(
        key = "refresh_token",
        value = refresh_token,
        httponly = True,
        secure = True,
        samesite = "strict",
        max_age = 60 * 60 * 24 * 7
    )

    return DataResponse().success_response(
        {
            'access_token': access_token
        }
    )