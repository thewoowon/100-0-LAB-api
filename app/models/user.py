from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(Base):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    # 0: 일반, 1: Google, 2: Kakao
    user_type = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Integer, nullable=False, default=0)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)

    videos = relationship("Video", back_populates="user")
    tokens = relationship("Token", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    submissions = relationship("VideoSubmission", back_populates="user")
    payout_accounts = relationship("PayoutAccount", back_populates="user")
