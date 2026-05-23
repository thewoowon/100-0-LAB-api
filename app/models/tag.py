from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Tag(Base):
    __tablename__ = "tag"

    video_id = Column(Integer, ForeignKey("video.id"), nullable=False)
    name = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("video_id", "name", name="uq_tag_video_name"),
    )

    video = relationship("Video", back_populates="tags")
