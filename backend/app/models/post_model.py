from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base_model import BareBaseModel

class Post(BareBaseModel):
    title = Column(String(255))
    content = Column(Text)
    like_count = Column(Integer, default = 0)
    author_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='post')
    comment = relationship('Comment', back_populates='post')
    like = relationship('Like', back_populates='post')