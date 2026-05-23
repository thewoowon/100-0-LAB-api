from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Vote(Base):
    __tablename__ = "vote"

    video_id = Column(Integer, ForeignKey("video.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    ratio = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("video_id", "user_id", name="uq_vote_video_user"),
    )

    video = relationship("Video", backref="votes")
    user = relationship("User", backref="votes")
