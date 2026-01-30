from app.models.base_model import BareBaseModel
from app.core.config import settings
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

class User(BareBaseModel):
    user_name = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    avatar = Column(String(255), default=f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/avatars/default.jpg")

    post = relationship('Post', back_populates='user')
    comment = relationship('Comment', back_populates='user')
    like = relationship('Like', back_populates='user')
    refresh_token = relationship('RefreshToken', back_populates='user')