from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from fastapi.encoders import jsonable_encoder

from app.helpers.login_manager import login_required, admin_required
from app.helpers.paging import Page, paginate, PaginationParams
from app.schemas.sche_comment import CommentCreateRequest, CommentResponse, ChangeMyCommentRequest
from app.schemas.sche_base import DataResponse
from app.models.user_model import User
from app.models.comment import Comment
from app.services.srv_user import UserService
from app.services.srv_comment import CommentService
from app.api.websocket import manager

router = APIRouter()

@router.post('', dependencies=[Depends(login_required)], response_model=DataResponse[CommentResponse])
async def comment(
    comment_data: CommentCreateRequest,
    current_user: User = Depends(UserService.get_current_user),
    comment_service: CommentService = Depends()
):
    try:
        comment = comment_service.comment(comment_data, current_user)
        comment.full_name = comment.user.full_name
        comment.avatar = comment.user.avatar
        comment.type = 'comment'
        await manager.broadcast(jsonable_encoder(comment))
        return DataResponse().success_response(comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.get('/me', dependencies=[Depends(login_required)], response_model=Page[CommentResponse])
def get_my_comment(
    current_user: User = Depends(UserService.get_current_user),
    params: PaginationParams = Depends()
):
    try:
        _query = db.session.query(Comment).filter(Comment.author_id == current_user.id)
        comments = paginate(Comment, _query, params)
        for comment in comments:
            comment.full_name = comment.user.full_name
            comment.avatar = comment.user.avatar
            comment.type = 'comment'
        return comments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.put('/me/{comment_id}', dependencies=[Depends(login_required)], response_model=DataResponse[CommentResponse])
def change_my_comment(
    comment_id: int,
    comment_data: ChangeMyCommentRequest,
    current_user: User = Depends(UserService.get_current_user),
    comment_service: CommentService = Depends()
):
    try:
        comment = comment_service.change_comment(comment_id, current_user, comment_data)
        comment.full_name = comment.user.full_name
        comment.avatar = comment.user.avatar
        comment.type = 'comment'
        return DataResponse().success_response(comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.delete('/me/{comment_id}', dependencies=[Depends(login_required)], response_model=DataResponse[CommentResponse])
def delete_my_comment(
    comment_id: int,
    current_user: User = Depends(UserService.get_current_user),
    comment_service: CommentService = Depends()
):
    try:
        comment = comment_service.delete_my_comment(comment_id, current_user)
        comment.full_name = comment.user.full_name
        comment.avatar = comment.user.avatar
        comment.type = 'comment'
        return DataResponse().success_response(comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    
@router.delete('/{comment_id}', dependencies=[Depends(admin_required)], response_model=DataResponse[CommentResponse])
def delete_my_comment(
    comment_id: int,
    comment_service: CommentService = Depends()
):
    try:
        comment = comment_service.delete_my_comment(comment_id)
        comment.full_name = comment.user.full_name
        comment.avatar = comment.user.avatar
        comment.type = 'comment'
        return DataResponse().success_response(comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )