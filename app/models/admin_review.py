import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class ReviewDecision(str, enum.Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
    DUPLICATE = "DUPLICATE"
    RIGHTS_RISK = "RIGHTS_RISK"


class AdminReview(Base):
    __tablename__ = "adminreview"

    submission_id = Column(Integer, ForeignKey("videosubmission.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    decision = Column(Enum(ReviewDecision), nullable=False)
    memo = Column(Text, nullable=True)
    rejection_reason = Column(String, nullable=True)

    checklist_playable = Column(Boolean, nullable=True)
    checklist_under_one_minute = Column(Boolean, nullable=True)
    checklist_likely_original = Column(Boolean, nullable=True)
    checklist_no_news_source = Column(Boolean, nullable=True)
    checklist_blur_possible = Column(Boolean, nullable=True)
    checklist_location_safe = Column(Boolean, nullable=True)
    checklist_not_sensitive = Column(Boolean, nullable=True)
    checklist_payout_eligible = Column(Boolean, nullable=True)

    submission = relationship("VideoSubmission", back_populates="admin_reviews")
    admin = relationship("User", foreign_keys=[admin_id])
