from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from typing import Any

from app.models.user_model import User
from app.models.post_model import Post
from app.models.like_model import Like
from app.schemas.sche_user import UserItemResponse, UserUpdateRequest, UserUpdateMeRequest, UserChangePasswordRequest
from app.schemas.sche_base import DataResponse
from app.schemas.sche_post import PostResponse
from app.services.srv_user import UserService
from app.helpers.login_manager import login_required, admin_required
from app.helpers.paging import Page, paginate, PaginationParams

router = APIRouter()

@router.get('', dependencies=[Depends(login_required)],response_model=Page[UserItemResponse])
def get_all_user(params: PaginationParams = Depends()):
    try:
        _query = db.session.query(User)
        users = paginate(User, _query, params)
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
    
@router.get("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail_me(current_user: User = Depends(UserService.get_current_user)):
    return DataResponse().success_response(current_user)

@router.get('/{user_id}/posts', dependencies=[Depends(login_required)], response_model=Page[PostResponse])
def get_all_post(
    user_id: int,
    params: PaginationParams = Depends()
):
    try:
        _query = db.session.query(Post).filter(Post.author_id == user_id)
        posts = paginate(Post, _query, params)
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('/{user_id}/liked-posts', dependencies=[Depends(login_required)], response_model=Page[PostResponse])
def get_user_liked(
    user_id: int,
    params: PaginationParams = Depends()
):
    try:
        _query = db.session.query(Post).join(Like).filter(Like.author_id == user_id)
        liked_posts = paginate(Like, _query, params)
        return liked_posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get("/{user_id}", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail(user_id: int, user_service: UserService = Depends()):
    try:
        return DataResponse().success_response(data=user_service.get(user_id))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
    
@router.put('/me', dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def update_me(
    new_data: UserUpdateMeRequest,
    current_user: User = Depends(UserService.get_current_user),
    user_service: UserService = Depends()
):
    try:
        user = user_service.update_me(current_user, new_data)
        return DataResponse().success_response(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )

@router.put('/me/password', dependencies=[Depends(login_required)])
def change_password(
    new_data: UserChangePasswordRequest,
    current_user: User = Depends(UserService.get_current_user),
    user_service: UserService = Depends()
):
    try:
        user = user_service.change_password(current_user, new_data)
        return "Password changed"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )

@router.put('/me/avatar', dependencies=[Depends(login_required)])
def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(UserService.get_current_user),
    user_service: UserService = Depends()
):
    try:
        avatar_url = user_service.upload_avatar(avatar, current_user)
        return avatar_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )

    
@router.put('/{user_id}', dependencies=[Depends(admin_required)], response_model=DataResponse[UserItemResponse])
def update(
    user_id: int,
    user_data: UserUpdateRequest,
    user_service: UserService = Depends()
):
    try:
        user = user_service.update(user_id, user_data)
        return DataResponse().success_response(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.delete('/{user_id}', dependencies=[Depends(admin_required)], response_model=DataResponse[UserItemResponse])
def delete_user(
    user_id: int,
    user_service: UserService = Depends()
):
    try:
        user = user_service.delete(user_id)
        return DataResponse().success_response(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )