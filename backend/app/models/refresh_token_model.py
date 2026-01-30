from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base_model import BareBaseModel

class RefreshToken(BareBaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    jti = Column(String(255), unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='refresh_token')
