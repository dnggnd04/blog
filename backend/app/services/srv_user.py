from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from fastapi import Depends, status, UploadFile
from pydantic import ValidationError
from uuid import uuid4
import jwt
from datetime import datetime, timezone

from app.schemas.sche_user import UserRegisterRequest, UserUpdateRequest, UserUpdateMeRequest, UserChangePasswordRequest
from app.models.user_model import User
from app.models.refresh_token_model import RefreshToken
from app.core.security import get_password_hash, verify_password
from app.core.config import settings, s3_avatar
from app.schemas.sche_token import TokenPayload
from app.core.security import create_refresh_token

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
        exist_email = db.session.query(User).filter(User.email == data.email).first()
        if exist_user_name or exist_email:
            raise HTTPException(status_code=400, detail="Email or username already exists")
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
    def save_refresh_token(user: User, refresh_token: str):
        
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            settings.SECURITY_ALGORITHM
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        new_refresh_token = RefreshToken(
            user_id = user.id,
            jti = jti,
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc),
            revoked = False
        )
        db.session.add(new_refresh_token)
        db.session.commit()
        return new_refresh_token
    
    @staticmethod
    def verify_refresh_token(user_name: str, jti: str):
        refresh_token = (
            db.session.query(RefreshToken)
            .join(User)
            .filter(
                User.user_name == user_name,
                RefreshToken.jti == jti
            )
            .first()
        )
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        if refresh_token.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Revoked refresh token"
            )
        expires_at = refresh_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired refresh token"
            )

        return refresh_token

    
    @staticmethod
    def rotate_refresh_token(user_name: str, old_jti: str, new_refresh_token: str):
        old_refresh_token = (
            db.session.query(RefreshToken)
            .join(User)
            .filter(
                User.user_name == user_name,
                RefreshToken.jti == old_jti
            )
            .first()
        )
        if not old_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        payload = jwt.decode(
            new_refresh_token,
            settings.SECRET_KEY,
            settings.SECURITY_ALGORITHM
        )

        new_jti = payload.get("jti")
        exp = payload.get("exp")

        if not new_jti or not exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        old_refresh_token.revoked = True
        old_refresh_token.revoked_at = datetime.now(timezone.utc)

        new_refresh_token_entry = RefreshToken(
            user_id = old_refresh_token.user_id,
            jti = new_jti,
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc),
            revoked = False
        )
        db.session.add(new_refresh_token_entry)
        db.session.commit()

    @staticmethod
    def revoke_all_refresh_tokens(user_id: int):
        refresh_tokens = (
            db.session.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
            .all()
        )
        for token in refresh_tokens:
            token.revoked = True
            token.revoked_at = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def get(user_id):
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise HTTPException(status_code=400, detail="User not exists")
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
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired"
            )
        except (jwt.InvalidTokenError, jwt.PyJWKError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user = db.session.query(User).filter(User.user_name == token_data.user_name).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
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