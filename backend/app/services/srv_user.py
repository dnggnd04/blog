from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from fastapi import Depends, status, UploadFile
from pydantic import ValidationError
from uuid import uuid4
import jwt

from app.schemas.sche_user import UserRegisterRequest, UserUpdateRequest, UserUpdateMeRequest, UserChangePasswordRequest
from app.models.user_model import User
from app.core.security import get_password_hash, verify_password
from app.core.config import settings, s3_avatar
from app.schemas.sche_token import TokenPayload

class UserService(object):
    _instance = None

    def __init__(self):
        pass

    reusable_oauth2 = HTTPBearer(
        scheme_name='Authorization'
    )

    @staticmethod
    def register_user(data: UserRegisterRequest):
        exist_user_name = db.session.query(User).filter(User.user_name == data.user_name).first()
        exist_email = db.session.query(User).filter(User.user_name == data.email).first()
        if exist_user_name or exist_email:
            raise Exception('Email or username already exists')
        register_user = User(
            user_name = data.user_name,
            email = data.email,
            full_name = data.full_name,
            is_admin = data.is_admin,
            hashed_password = get_password_hash(data.password),
            is_active = True
        )
        db.session.add(register_user)
        db.session.commit()
        return register_user
    
    @staticmethod
    def get(user_id):
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise Exception('User not exists')
        return exist_user
    
    @staticmethod
    def authenticate(*, user_name: str, password: str):
        user = db.session.query(User).filter(User.user_name == user_name).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username doesn't exist"
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        return user


    @staticmethod
    def get_current_user(http_authorization_credentials=Depends(reusable_oauth2)) -> User:
        try:
            payload = jwt.decode(
                http_authorization_credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.SECURITY_ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (jwt.PyJWKError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Could not validate credentials"
            )
        user = db.session.query(User).filter(User.user_name == token_data.user_name).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def change_password(current_user: User, new_data: UserChangePasswordRequest):
        if not verify_password(new_data.old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong password"
            )
        current_user.hashed_password = get_password_hash(new_data.new_password)
        db.session.commit()
        return current_user
    
    @staticmethod
    def update_me(current_user: User, new_data: UserUpdateMeRequest):
        current_user.full_name = new_data.full_name if new_data.full_name is not None else current_user.full_name
        db.session.commit()
        return current_user
    
    @staticmethod
    def update(user_id: int, user_data: UserUpdateRequest):
        user = db.session.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id"
            )
        user.full_name = user_data.full_name if user_data.full_name is not None else user.full_name
        user.email = user_data.email if user_data.email is not None else user.email
        user.password = user_data.password if user_data.password is not None else user.password
        user.is_active = user_data.is_active if user_data.is_active is not None else user.is_active
        user.is_admin = user_data.is_admin if user_data.is_admin is not None else user.is_admin
        db.session.commit()
        return user
    
    @staticmethod
    def upload_avatar(avatar, current_user: User):
        try:
            file_ext = avatar.filename.split('.')[-1]
            key = f"avatars/{current_user.id}.{file_ext}"
            s3_avatar.upload_fileobj(avatar.file, settings.AWS_BUCKET_NAME, key, ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'image/jpeg'
            })
            url = f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"

            current_user.avatar = url
            db.session.commit()
            return url

        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def delete(user_id: int):
        user = db.session.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid id"
            )
        db.session.delete(user)
        db.session.commit()
        return user