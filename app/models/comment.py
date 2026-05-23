from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Comment(Base):
    __tablename__ = "comment"

    video_id = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    is_party = Column(Boolean, nullable=False, default=False)   # 당사자 여부
    party_role = Column(String, nullable=True)                  # "가해자" / "피해자" / "목격자"
    party_verified = Column(Boolean, nullable=False, default=False)  # 업로더 인증 여부
    created_at = Column(DateTime, server_default=func.now())

    video = relationship("Video", back_populates="comments")
    user = relationship("User", back_populates="comments")
