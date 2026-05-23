from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    # 0: 일반, 1: Google, 2: Kakao
    user_type = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Integer, nullable=False, default=0)

    videos = relationship("Video", back_populates="user")
    tokens = relationship("Token", back_populates="user")
    comments = relationship("Comment", back_populates="user")
