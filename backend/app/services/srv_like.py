from pydantic import BaseModel
from fastapi_sqlalchemy import db
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from app.schemas.sche_like import LikeModel
from app.models.user_model import User
from app.models.like_model import Like
from app.models.post_model import Post

class LikeService(object):

    @staticmethod
    def like(like_data: LikeModel, current_user: User):
        post = db.session.query(Post).get(like_data.post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid post id"
            )
        like = db.session.query(Like).filter(Like.author_id == current_user.id, Like.post_id == like_data.post_id).first()
        if like:
            db.session.delete(like)
            post.like_count -= 1
            db.session.commit()
        else:
            new_like = Like(
                author_id = current_user.id,
                post_id = like_data.post_id
            )
            db.session.add(new_like)
            post.like_count += 1
            db.session.commit()
        return post.like_count