from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_sqlalchemy import db

from app.schemas.sche_post import PostRequest, PostResponse, UpdateMyPostRequest, UpdatePostRequest
from app.schemas.sche_comment import CommentResponse
from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import UserItemResponse
from app.models.user_model import User
from app.models.post_model import Post
from app.models.like_model import Like
from app.models.comment import Comment
from app.services.srv_user import UserService
from app.services.srv_post import PostService
from app.helpers.paging import Page, PaginationParams, paginate
from app.helpers.login_manager import login_required, admin_required

router = APIRouter()

@router.post('', dependencies=[Depends(login_required)], response_model=DataResponse[PostResponse])
def create_post(
    post_data: PostRequest,
    current_user: User = Depends(UserService.get_current_user),
    post_service: PostService = Depends()
):
    try:
        post = post_service.create_post(current_user, post_data)
        post.full_name = post.user.full_name
        post.avatar = post.user.avatar
        return DataResponse().success_response(post)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('', dependencies=[Depends(login_required)], response_model=Page[PostResponse])
def get_user_post(
    params: PaginationParams = Depends()
):
    try:
        _query = db.session.query(Post)
        posts = paginate(Post, _query, params)
        for post in posts.data:
            post.full_name = post.user.full_name
            post.avatar = post.user.avatar
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('/me', dependencies=[Depends(login_required)], response_model=Page[PostResponse])
def get_all_post(
    params: PaginationParams = Depends(),
    current_user: User = Depends(UserService.get_current_user)
):
    try:
        _query = db.session.query(Post).filter(Post.author_id == current_user.id)
        posts = paginate(Post, _query, params)
        for post in posts.data:
            post.full_name = post.user.full_name
            post.avatar = post.user.avatar
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('/{post_id}/comments', dependencies=[Depends(login_required)], response_model=Page[CommentResponse])
def get_post_comment(
    post_id: int,
    params: PaginationParams = Depends()
):
    try:
        _query = db.session.query(Comment).filter(Comment.post_id == post_id)
        comments = paginate(Comment, _query, params)
        for comment in comments.data:
            comment.full_name = comment.user.full_name
            comment.avatar = comment.user.avatar
            comment.type = 'comment'

        return comments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('/{post_id}/likes/users', dependencies=[Depends(login_required)], response_model=Page[UserItemResponse])
def get_post_liked(
    post_id: int,
    params: PaginationParams = Depends()
):
    try:
        _query = db.session.query(User).join(Like).filter(Like.post_id == post_id)
        liked_user = paginate(Like, _query, params)
        return liked_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('/{post_id}', dependencies=[Depends(login_required)], response_model=DataResponse[PostResponse])
def get_post(
    post_id: int,
    post_service: PostService = Depends()
):
    try:
        post = post_service.get_post(post_id)
        post.full_name = post.user.full_name
        post.avatar = post.user.avatar
        return DataResponse().success_response(post)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.put('/me/{post_id}', dependencies=[Depends(login_required)], response_model=DataResponse[PostResponse])
def update_my_post(
    post_id: int,
    new_data: UpdateMyPostRequest,
    current_user: User = Depends(UserService.get_current_user),
    post_service: PostService = Depends()
):
    try:
        post = post_service.update_my_post(post_id, current_user, new_data)
        post.full_name = post.user.full_name
        post.avatar = post.user.avatar
        return DataResponse().success_response(post)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail
            )
    
@router.put('/{post_id}', dependencies=[Depends(admin_required)], response_model=DataResponse[PostResponse])
def update_post(
    post_id: int,
    new_data: UpdatePostRequest,
    post_service: PostService = Depends()
):
    try:
        post = post_service.update_post(post_id, new_data)
        post.full_name = post.user.full_name
        post.avatar = post.user.avatar
        return DataResponse().success_response(post)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail
            )
    
@router.delete('/{post_id}', dependencies=[Depends(admin_required)], response_model=DataResponse[PostResponse])
def delete_post(
    post_id: int,
    post_service: PostService = Depends()
):
    try:
        post = post_service.delete_post(post_id)
        post.full_name = post.user.full_name
        post.avatar = post.user.avatar
        return DataResponse().success_response(post)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail
            )
    
