from fastapi_sqlalchemy import db
from fastapi.exceptions import HTTPException
from fastapi import status

from app.models.user_model import User
from app.models.post_model import Post
from app.schemas.sche_post import PostRequest, UpdateMyPostRequest, UpdatePostRequest

class PostService(object):

    @staticmethod
    def create_post(current_user: User, post_data: PostRequest):
        post = Post(
            title = post_data.title,
            content = post_data.content,
            user = current_user
        )
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def get_post(post_id: int):
        post = db.session.query(Post).get(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid id"
            )
        return post
    
    @staticmethod
    def update_my_post(post_id: int, current_user: User, new_data: UpdateMyPostRequest):
        post = db.session.query(Post).get(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid id"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You don't own this post"
            )
        post.title = new_data.title if new_data.title is not None else post.title
        post.content = new_data.content if new_data.content is not None else post.content
        db.session.commit()
        return post
    
    @staticmethod
    def update_post(post_id: int, new_data: UpdatePostRequest):
        post = db.session.query(Post).get(post_id)
        user = db.session.query(User).get(new_data.author_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid post id"
            )
        post.title = new_data.title if new_data.title is not None else post.title
        post.content = new_data.content if new_data.content is not None else post.content
        post.user = user if user is not None else post.user
        db.session.commit()
        return post
    
    @staticmethod
    def delete_post(post_id: int):
        post = db.session.query(Post).get(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid post id"
            )
        db.session.delete(post)
        db.session.commit()
        return post