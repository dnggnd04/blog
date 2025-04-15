from app.models.base_model import BareBaseModel
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

class Like(BareBaseModel):
    post_id = Column(Integer, ForeignKey('post.id'))
    author_id = Column(Integer, ForeignKey('user.id'))
    
    post = relationship('Post', back_populates='like')
    user = relationship('User', back_populates='like')