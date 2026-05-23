from sqlalchemy import Column, Integer, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from app.db.base import Base


class VideoEmbedding(Base):
    __tablename__ = "videoembedding"

    video_id = Column(Integer, ForeignKey("video.id"), unique=True, nullable=False)
    embedding = Column(LargeBinary, nullable=False)

    video = relationship("Video", back_populates="embedding")
