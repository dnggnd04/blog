from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from fastapi.encoders import jsonable_encoder

from app.schemas.sche_like import LikeModel
from app.schemas.sche_post import PostResponse
from app.schemas.sche_user import UserItemResponse
from app.schemas.sche_base import DataResponse
from app.models.user_model import User
from app.models.like_model import Like
from app.models.post_model import Post
from app.helpers.login_manager import login_required
from app.helpers.paging import Page, paginate, PaginationParams
from app.services.srv_user import UserService
from app.services.srv_like import LikeService
from app.api.websocket import manager

router = APIRouter()

@router.post('', dependencies=[Depends(login_required)])
async def like(
    like_data: LikeModel,
    current_user: User = Depends(UserService.get_current_user),
    like_service: LikeService = Depends()
):
    try:
        like_count = like_service.like(like_data, current_user)
        await manager.broadcast({
            "type": "like",
            "post_id": like_data.post_id,
            "like_count": like_count
        })
        return jsonable_encoder(like_count)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )