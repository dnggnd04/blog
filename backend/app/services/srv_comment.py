from fastapi_sqlalchemy import db
from fastapi import status
from fastapi.exceptions import HTTPException

from app.schemas.sche_comment import CommentCreateRequest, ChangeMyCommentRequest
from app.models.user_model import User
from app.models.comment import Comment
from app.models.post_model import Post
from app.helpers.paging import paginate, PaginationParams

class CommentService(object):

    @staticmethod
    def comment(comment_data: CommentCreateRequest, current_user: User):
        post = db.session.query(Post).get(comment_data.post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid post id"
            )
        comment = Comment(
            content = comment_data.content,
            post_id = comment_data.post_id,
            author_id = comment_data.author_id if comment_data.author_id is not None else current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        return comment
    
    @staticmethod
    def change_comment(comment_id: int, current_user: User, comment_data: ChangeMyCommentRequest):
        comment = db.session.query(Comment).get(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid comment id"
            )
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User doesn't own this comment"
            )
        comment.content = comment_data.content
        db.session.commit()
        return comment
    
    @staticmethod
    def delete_my_comment(comment_id: int, current_user: User = None):
        comment = db.session.query(Comment).get(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid comment id"
            )
        if current_user is not None and comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User doesn't own this comment"
            )
        db.session.delete(comment)
        db.session.commit()
        return comment