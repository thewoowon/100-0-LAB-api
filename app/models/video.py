from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base


class Video(Base):
    __tablename__ = "video"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    views = Column(Integer, nullable=False, default=0)
    filmed_date = Column(Date, nullable=True)
    filmed_location = Column(String, nullable=True)

    user = relationship("User", back_populates="videos")
    tags = relationship("Tag", back_populates="video", cascade="all, delete-orphan")
    embedding = relationship("VideoEmbedding", back_populates="video", uselist=False)
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
