from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CaseStatus(Base):
    __tablename__ = "casestatus"

    video_id = Column(Integer, ForeignKey("video.id"), unique=True, nullable=False)
    status = Column(String, nullable=False, default="알_수_없음")
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    actual_ratio = Column(String, nullable=True)       # 공식 과실 비율 e.g. "100:0"
    resolution_note = Column(String, nullable=True)    # 결론 메모

    video = relationship("Video", backref="case_status")
    updater = relationship("User", backref="case_status_updates")
