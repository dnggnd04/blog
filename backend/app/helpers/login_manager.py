from fastapi import Depends, status
from fastapi.exceptions import HTTPException

from app.models.user_model import User
from app.services.srv_user import UserService

def login_required(http_authorization_credentials=Depends(UserService().reusable_oauth2)):
    return UserService().get_current_user(http_authorization_credentials)

def admin_required(user: User = Depends(login_required)):
    if not user.is_admin:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail=f"User {user.user_name} can not access this api"
        )