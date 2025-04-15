from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import UserRegisterRequest, UserItemResponse
from app.services.srv_user import UserService

router = APIRouter()

@router.post('', response_model=DataResponse[UserItemResponse])
def register(
    register_data: UserRegisterRequest,
    user_service: UserService = Depends()
):
    try:
        user_register = user_service.register_user(register_data)
        return DataResponse().success_response(user_register)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))