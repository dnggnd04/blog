from app.models.base_model import BareBaseModel
from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Comment(BareBaseModel):
    content = Column(Text)
    post_id = Column(Integer, ForeignKey('post.id'))
    author_id = Column(Integer, ForeignKey('user.id'))

    post = relationship('Post', back_populates='comment')
    user = relationship('User', back_populates='comment')